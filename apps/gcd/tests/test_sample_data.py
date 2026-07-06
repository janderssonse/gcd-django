# -*- coding: utf-8 -*-
"""
The `sample_data` command must build a graph that is valid by
construction and leaves the public detail pages clickable, so a fresh dev
DB is populated without a login-gated production dump. These tests are the
executable form of that promise: run the command and render the pages.
"""

import pytest
from django.core.management import call_command

from apps.gcd.models import Publisher, Series, Issue, Story, Creator

BASE = 990000


@pytest.mark.django_db
def test_sample_data_is_idempotent():
    # Fixed PKs + get_or_create: running it twice must not duplicate or
    # raise, so re-seeding a dev DB is always safe.
    call_command('sample_data')
    call_command('sample_data')

    assert Publisher.objects.filter(id__gte=BASE).count() == 2
    assert Series.objects.filter(id__gte=BASE).count() == 3
    assert Issue.objects.filter(id__gte=BASE).count() == 6
    assert Story.objects.filter(id__gte=BASE).count() == 6


@pytest.mark.django_db
def test_sample_story_has_full_credit_graph():
    call_command('sample_data')

    story = Story.objects.filter(id__gte=BASE).first()
    # One linked StoryCredit per credit type, plus the plaintext mirror the
    # credits templatetag reads.
    assert story.credits.count() == 6
    assert {c.credit_type.name for c in story.credits.all()} == {
        'script', 'pencils', 'inks', 'colors', 'letters', 'editing'}
    assert story.script  # plaintext credit populated


@pytest.mark.django_db
@pytest.mark.parametrize('model, pk', [
    (Publisher, BASE + 1),
    (Series, BASE + 1),
    (Issue, (BASE + 1) * 100),
    (Creator, BASE + 1),
])
def test_sample_detail_pages_render(client, model, pk):
    # The whole point of the sample graph: the hot public pages are
    # clickable out of the box. A missing date/name detail (e.g. the
    # creator page dereferencing death_date) would 500 here.
    call_command('sample_data')

    response = client.get(model.objects.get(id=pk).get_absolute_url())

    assert response.status_code == 200
