# -*- coding: utf-8 -*-
"""
Characterization coverage for the OI changeset compare/preview pages
(roadmap A5).

compare() renders the field-by-field diff for a changeset and preview()
renders a revision as its display object; between them they drive a large
part of apps/oi -- field_list(), compare_changes(), the Preview proxies, the
reflection layer -- with almost no coverage until now. They are the safety
net for the C1 god-module split: these tests pin that both pages render for
each major add change type, so a refactor that breaks the render fails here.
"""

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from apps.oi.models import CTYPES

# Fixtures for a single added revision whose compare page renders inline.
INLINE_ADD_FIXTURES = [
    'any_added_publisher_rev',
    'any_added_series_rev',
    'any_added_brand_rev',
    'any_added_indicia_publisher_rev',
]


@pytest.fixture
def reserver_client(client, any_indexer):
    """A logged-in indexer (the changeset's own indexer in these fixtures)."""
    any_indexer.user_permissions.add(
        Permission.objects.get(content_type__app_label='indexer',
                               codename='can_reserve'))
    client.force_login(any_indexer)
    return client


def _retype_changeset(revision):
    """The add fixtures share a changeset with an arbitrary change_type
    (conftest hardcodes 'publisher'); point it at the revision's real type so
    compare() dispatches to the right revision, and return it."""
    changeset = revision.changeset
    changeset.change_type = CTYPES[revision.source_name]
    changeset.save()
    return changeset


@pytest.mark.django_db
@pytest.mark.parametrize('rev_fixture', INLINE_ADD_FIXTURES)
def test_compare_add_renders(reserver_client, request, rev_fixture):
    revision = request.getfixturevalue(rev_fixture)
    changeset = _retype_changeset(revision)

    response = reserver_client.get(reverse('compare', args=[changeset.id]))

    assert response.status_code == 200


@pytest.mark.django_db
def test_compare_issue_add_renders(reserver_client, any_added_issue_rev):
    changeset = any_added_issue_rev.changeset
    changeset.change_type = CTYPES['issue_add']
    changeset.save()

    response = reserver_client.get(reverse('compare', args=[changeset.id]))

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize('rev_fixture', INLINE_ADD_FIXTURES)
def test_preview_renders(reserver_client, request, rev_fixture):
    revision = request.getfixturevalue(rev_fixture)

    response = reserver_client.get(reverse(
        'preview_revision',
        kwargs={'model_name': revision.source_name, 'id': revision.id}))

    assert response.status_code == 200
