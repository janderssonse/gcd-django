# -*- coding: utf-8 -*-
"""
The structural parent links (Series.publisher, Issue.series, Story.issue)
use on_delete=PROTECT (roadmap B2). Removal is meant to go through the
soft-delete flag; a stray *hard* delete of a parent must raise rather than
silently cascade-wipe its subtree. These pin that behaviour.
"""

import pytest
from django.db.models import ProtectedError

from apps.gcd.models import Publisher, Series, Issue, Story, StoryType
from apps.stddata.models import Country, Language


@pytest.fixture
def graph(db):
    country, _ = Country.objects.get_or_create(code='zz',
                                               defaults={'name': 'Zedland'})
    language, _ = Language.objects.get_or_create(code='zz',
                                                 defaults={'name': 'Zed'})
    publisher = Publisher.objects.create(name='P', country=country,
                                         year_began=1990)
    series = Series.objects.create(
        name='S', sort_name='S', year_began=1990, country=country,
        language=language, publisher=publisher, is_comics_publication=True)
    issue = Issue.objects.create(number='1', series=series, sort_code=0)
    story = Story.objects.create(
        issue=issue, type=StoryType.objects.get(name='comic story'),
        sequence_number=0)
    return publisher, series, issue, story


@pytest.mark.django_db
def test_hard_delete_publisher_with_series_is_blocked(graph):
    publisher = graph[0]
    with pytest.raises(ProtectedError):
        Publisher.objects.filter(pk=publisher.pk).delete()


@pytest.mark.django_db
def test_hard_delete_series_with_issues_is_blocked(graph):
    series = graph[1]
    with pytest.raises(ProtectedError):
        Series.objects.filter(pk=series.pk).delete()


@pytest.mark.django_db
def test_hard_delete_issue_with_stories_is_blocked(graph):
    issue = graph[2]
    with pytest.raises(ProtectedError):
        Issue.objects.filter(pk=issue.pk).delete()


@pytest.mark.django_db
def test_soft_delete_still_works(graph):
    # The intended path is unaffected: instance.delete() just sets the flag.
    issue = graph[2]
    issue.delete()
    issue.refresh_from_db()
    assert issue.deleted is True
