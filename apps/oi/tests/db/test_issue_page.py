# -*- coding: utf-8 -*-
"""
Performance/behaviour coverage for the public issue detail page.

The most-viewed public page had only the zero-story characterization
snapshot. These tests render it with real story sequences and guard
against per-story query scaling (N+1).
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.gcd.models import Story, StoryType


def _add_stories(issue, count):
    story_type = StoryType.objects.get(name='comic story')
    for i in range(count):
        Story.objects.create(issue=issue, type=story_type,
                             sequence_number=i + 1, page_count=1,
                             script='Writer %d' % i, pencils='Artist %d' % i)


def _issue_page_query_count(client, issue):
    url = reverse('show_issue', kwargs={'issue_id': issue.id})
    with CaptureQueriesContext(connection) as ctx:
        response = client.get(url)
    assert response.status_code == 200
    return len(ctx.captured_queries)


@pytest.mark.django_db
def test_issue_page_renders_with_stories(client, any_added_issue):
    _add_stories(any_added_issue, 3)

    response = client.get(
        reverse('show_issue', kwargs={'issue_id': any_added_issue.id}))

    assert response.status_code == 200


@pytest.mark.django_db
def test_issue_page_has_bounded_per_story_queries(client, any_added_issue):
    # Render the page with a few and with many stories; the extra queries per
    # additional story must stay small. Guards the shown_stories prefetching
    # against N+1 regressions (see roadmap P3).
    _add_stories(any_added_issue, 1)
    few = _issue_page_query_count(client, any_added_issue)

    _add_stories(any_added_issue, 4)  # five stories total now
    many = _issue_page_query_count(client, any_added_issue)

    # The page currently costs ~5 queries per extra story (the remaining
    # character/reprint N+1s are roadmap P3). Lock that in: any *added*
    # per-story query (e.g. dropping a shown_stories prefetch) must fail.
    per_story = (many - few) / 4
    assert per_story <= 5, (
        'issue page runs %.1f queries per extra story (%d -> %d); '
        'a story relation is no longer prefetched' % (per_story, few, many))
