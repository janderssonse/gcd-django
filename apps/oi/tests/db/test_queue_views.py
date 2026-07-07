# -*- coding: utf-8 -*-
"""
Behaviour tests for the editorial queue view (apps.oi.views.show_queue).

The view had no coverage, yet it drives the whole indexing workflow and
builds ~30 per-change-type querysets. These tests assert the observable
behaviour -- which changesets land in which queue -- and, because rendering
evaluates every bucket queryset, they also guard the select_related/
prefetch_related lookups against a mistyped relation name.
"""

import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from apps.oi import states
from apps.oi.models import Changeset, CTYPES
from apps.oi.views import _revision_accessor
from apps.indexer.models import Indexer


@pytest.fixture
def reserver_client(client, any_indexer):
    """A logged-in indexer allowed to see the queues."""
    any_indexer.user_permissions.add(
        Permission.objects.get(content_type__app_label='indexer',
                               codename='can_reserve'))
    client.force_login(any_indexer)
    return client


def changesets_in_bucket(response, object_type):
    """The changesets the queue rendered for one change type."""
    for bucket in response.context['data']:
        if bucket['object_type'] == object_type:
            return list(bucket['changesets'])
    return []


@pytest.mark.django_db
def test_editing_queue_lists_own_open_changeset(reserver_client,
                                                any_added_publisher_rev):
    changeset = any_added_publisher_rev.changeset  # OPEN, our indexer

    response = reserver_client.get(reverse('editing'))

    assert response.status_code == 200
    assert changeset in changesets_in_bucket(response, 'publisher')


@pytest.mark.django_db
def test_editing_queue_hides_other_indexers_changeset(reserver_client,
                                                      any_country,
                                                      any_added_publisher_rev):
    other_user = User.objects.create_user('other_indexer', password='x')
    Indexer.objects.create(user=other_user, country=any_country)
    other_changeset = Changeset.objects.create(
        state=states.OPEN, indexer=other_user,
        change_type=CTYPES['publisher'])

    response = reserver_client.get(reverse('editing'))

    bucket = changesets_in_bucket(response, 'publisher')
    assert any_added_publisher_rev.changeset in bucket
    assert other_changeset not in bucket


@pytest.mark.django_db
def test_editing_queue_hides_approved_changeset(reserver_client,
                                                any_added_publisher_rev):
    changeset = any_added_publisher_rev.changeset
    changeset.state = states.APPROVED  # no longer being edited
    changeset.save()

    response = reserver_client.get(reverse('editing'))

    assert changeset not in changesets_in_bucket(response, 'publisher')


@pytest.mark.django_db
def test_pending_queue_lists_pending_changeset(reserver_client,
                                               any_added_publisher_rev):
    changeset = any_added_publisher_rev.changeset
    changeset.state = states.PENDING
    changeset.save()

    response = reserver_client.get(reverse('pending'))

    assert response.status_code == 200
    assert changeset in changesets_in_bucket(response, 'publisher')


@pytest.mark.django_db
def test_reviews_queue_lists_changeset_assigned_to_approver(
        reserver_client, any_indexer, any_added_publisher_rev):
    changeset = any_added_publisher_rev.changeset
    changeset.approver = any_indexer
    changeset.state = states.REVIEWING
    changeset.save()

    response = reserver_client.get(reverse('reviewing'))

    assert response.status_code == 200
    assert changeset in changesets_in_bucket(response, 'publisher')


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['editing', 'pending', 'reviewing'])
def test_queue_renders_every_bucket(reserver_client, any_added_publisher_rev,
                                    url_name):
    # Rendering iterates and evaluates every per-change-type queryset, so a
    # bad select_related/prefetch_related lookup on any bucket raises here.
    response = reserver_client.get(reverse(url_name))

    assert response.status_code == 200
    assert response.context['data']


@pytest.mark.django_db
def test_queue_requires_permission(client, any_indexer):
    # Without can_reserve the queue is not accessible (redirect to login).
    client.force_login(any_indexer)

    response = client.get(reverse('editing'))

    assert response.status_code == 302


def test_every_change_type_prefetch_path_resolves():
    # show_queue prefetches each bucket as '<accessor>__previous_revision'
    # via _revision_accessor. Empty buckets skip prefetch validation at
    # runtime, so verify the whole two-hop path here: a wrong accessor or a
    # revision class missing previous_revision fails loudly.
    for change_type in CTYPES:
        if change_type == 'unknown':
            continue
        accessor = _revision_accessor(change_type)
        revision_relation = Changeset._meta.get_field(accessor)
        revision_relation.related_model._meta.get_field('previous_revision')


@pytest.mark.django_db
def test_editing_queue_query_count_is_bounded(reserver_client,
                                              django_assert_max_num_queries,
                                              any_added_publisher_rev):
    # A guard against gross N+1 regressions in the queue's bucket queries.
    with django_assert_max_num_queries(60):
        response = reserver_client.get(reverse('editing'))

    assert response.status_code == 200
