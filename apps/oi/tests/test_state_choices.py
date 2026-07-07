# -*- coding: utf-8 -*-
"""
The changeset state/type and issue index-status fields use IntegerChoices
enums as the single source of truth. The historical dict/constant names
(CTYPES, states.*, INDEXED) are kept as derived aliases; these tests guard
that the aliases stay in sync with the enums and that get_*_display works.
"""

from apps.oi import states
from apps.oi.models import CTYPES, ChangeType, Changeset
from apps.gcd.models.issue import INDEXED, IndexStatus, Issue


def test_ctypes_alias_matches_changetype_enum():
    # change_type values are persisted in the DB, so guard against renames
    # (the full key set) and renumbering (spot values across the range).
    assert set(CTYPES) == {
        'unknown', 'publisher', 'brand', 'indicia_publisher', 'series',
        'issue_add', 'issue', 'cover', 'issue_bulk', 'variant_add',
        'two_issues', 'reprint', 'image', 'brand_group', 'brand_use',
        'series_bond', 'creator', 'creator_art_influence', 'received_award',
        'creator_degree', 'creator_membership', 'creator_non_comic_work',
        'creator_relation', 'creator_school', 'award', 'feature',
        'feature_logo', 'feature_relation', 'printer', 'indicia_printer',
        'creator_signature', 'character', 'group', 'group_membership',
        'character_relation', 'group_relation', 'universe', 'story_arc',
        'story_arc_relation'}
    assert (CTYPES['unknown'], CTYPES['issue'], CTYPES['creator'],
            CTYPES['story_arc_relation']) == (0, 6, 16, 38)
    assert len(CTYPES) == len(ChangeType)


def test_states_aliases_match_enum():
    assert states.OPEN == states.ChangesetState.OPEN == 1
    assert states.UNRESERVED == 99
    assert states.ACTIVE == (1, 2, 3, 4)
    assert states.CLOSED == (5, 6)
    assert states.DISPLAY_NAME[states.APPROVED] == 'Approved'


def test_indexed_alias_matches_enum():
    # is_indexed values are persisted; assert the name->int contract
    # explicitly (IntegerChoices members compare equal to their ints).
    assert INDEXED == {'skeleton': 0, 'some_data': 1, 'partial': 2,
                       'ten_percent': 3, 'full': 10}


def test_get_display_methods():
    assert Changeset(
        change_type=CTYPES['issue']).get_change_type_display() == 'Issue'
    assert Changeset(state=states.OPEN).get_state_display() == 'Editing'
    assert Issue(is_indexed=INDEXED['full']).get_is_indexed_display() == 'Full'
