# -*- coding: utf-8 -*-
"""
Guards for the revision reflection layer (roadmap B0).

Field identity in the revision system is expressed as name strings matched
to model attributes at runtime, so a rename silently becomes a no-op. These
tests make that class of drift fail loudly instead.
"""

import pytest

from apps.oi.models import (
    validate_revision_definitions, Changeset, PublisherRevision,
)


def test_all_revision_field_paths_resolve():
    # Every parent/major-flag/stats path on every revision class must still
    # point at real fields. A stale name here breaks count/stat propagation.
    errors = validate_revision_definitions()
    assert errors == [], 'stale revision field paths:\n%s' % '\n'.join(errors)


def test_clone_rejects_unknown_exclude():
    # The exclude guard fires before any DB access, so this needs no data.
    with pytest.raises(ValueError):
        PublisherRevision.clone(data_object=None, changeset=None,
                                exclude={'definitely_not_a_field'})


def test_clone_accepts_real_field_in_exclude():
    # A real field name must not trip the guard (it fails later for lack of
    # a data object, but not with the guard's ValueError about field names).
    with pytest.raises(Exception) as info:
        PublisherRevision.clone(data_object=None, changeset=None,
                                exclude={'name'})
    assert 'not fields' not in str(info.value)


def test_revision_sets_rejects_unknown_change_type():
    with pytest.raises(ValueError):
        Changeset(change_type=9999)._revision_sets()
