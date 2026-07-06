# -*- coding: utf-8 -*-
"""
Regression tests for the advanced story search query builder.
"""

from functools import reduce
import operator

import pytest

from apps.stddata.models import Country, Language, Script
from apps.gcd.models import (
    Publisher, Series, Issue, Story, StoryType, StoryCredit, CreditType,
)
from apps.gcd.models.creator import Creator, CreatorNameDetail
from apps.gcd.models.story import CREDIT_TYPES
from apps.gcd.views.search import search_stories


# search_stories reads many form fields; default them all to "empty" and
# let each test override only what it exercises.
def _blank_search_data(**overrides):
    data = {
        'target': 'sequence',
        'logic': False,
        'credit_is_linked': None,
        'script': '', 'pencils': '', 'inks': '', 'colors': '', 'letters': '',
        'story_editing': '', 'issue_editing': '',
        'feature': '', 'feature_is_linked': None,
        'genre': [], 'type': [],
        'pages': '', 'pages_uncertain': None,
        'story_reprinted': '',
        'title': '', 'first_line': '', 'job_number': '',
        'characters': '', 'synopsis': '', 'reprint_notes': '', 'notes': '',
    }
    data.update(overrides)
    return data


@pytest.fixture
def editing_vs_letters(db):
    """One creator credited as editor on one story and as letterer on
    another, so a credit-type filter must discriminate between them."""
    script = Script.objects.get_or_create(
        id=Script.LATIN_PK,
        defaults={'code': 'Latn', 'number': Script.LATIN_PK,
                  'name': 'Latin'})[0]
    editing = CreditType.objects.get_or_create(
        id=CREDIT_TYPES['editing'],
        defaults={'name': 'editing', 'sort_code': CREDIT_TYPES['editing']})[0]
    letters = CreditType.objects.get_or_create(
        id=CREDIT_TYPES['letters'],
        defaults={'name': 'letters', 'sort_code': CREDIT_TYPES['letters']})[0]

    story_type = StoryType.objects.get_or_create(
        name='test-sequence', defaults={'sort_code': 99001})[0]
    country = Country.objects.get_or_create(
        id=902, defaults={'code': 'zs', 'name': 'Searchland'})[0]
    language = Language.objects.get_or_create(
        id=902, defaults={'code': 'zs', 'name': 'Searchish'})[0]
    publisher = Publisher.objects.create(
        name='Search Publisher', country=country, year_began=1950)
    series = Series.objects.create(
        name='Search Series', sort_name='Search Series', year_began=1950,
        country=country, language=language, publisher=publisher,
        is_comics_publication=True, has_gallery=False,
        publication_dates='1950')
    issue = Issue.objects.create(
        number='1', series=series, sort_code=0,
        publication_date='1950', key_date='1950-01-00')

    creator = Creator.objects.create(
        gcd_official_name='Search Person', sort_name='Search Person')
    name_detail = CreatorNameDetail.objects.create(
        name='Search Person', creator=creator, in_script=script)

    def make_story(credit_type):
        story = Story.objects.create(
            issue=issue, type=story_type, sequence_number=0)
        StoryCredit.objects.create(
            creator=name_detail, credit_type=credit_type, story=story)
        return story

    return make_story(editing), make_story(letters)


@pytest.mark.django_db
def test_story_editing_search_matches_only_editing_credits(editing_vs_letters):
    # Regression: the editing branch used a leaked loop variable as the
    # credit-type key, so it filtered on 'letters' instead of 'editing'
    # and returned the wrong stories.
    editing_story, letters_story = editing_vs_letters

    data = _blank_search_data(story_editing='Search Person')
    _text, linked_credits_q_objs, _q = search_stories(data, 'icontains')

    assert linked_credits_q_objs, 'expected a linked editing-credit query'
    query = reduce(operator.and_, linked_credits_q_objs)
    matched = set(Story.objects.filter(query).values_list('id', flat=True))

    assert matched == {editing_story.id}
