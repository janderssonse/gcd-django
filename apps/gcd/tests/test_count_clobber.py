# -*- coding: utf-8 -*-
"""
`update_cached_counts()` sets an ``F()`` expression on a cached-count
column, but the caller used to persist it with a full-row ``save()`` --
which writes back the in-memory (stale) values of *every other* column,
clobbering a concurrent edit to the same row (roadmap P5). It now returns
the set of count fields it touched and the caller saves only those, so the
atomic ``F()`` update cannot lose a concurrent change. These pin that.
"""

import pytest

from apps.gcd.models import Publisher
from apps.stddata.models import Country


@pytest.fixture
def publisher(db):
    country, _ = Country.objects.get_or_create(
        code='zz', defaults={'name': 'Zedland'})
    return Publisher.objects.create(name='Orig', country=country,
                                    year_began=1990)


@pytest.mark.django_db
def test_update_cached_counts_reports_touched_fields(publisher):
    # Only a count column with a non-zero delta is reported...
    assert publisher.update_cached_counts({'issues': 3}) == {'issue_count'}
    # ...and a zero delta touches nothing, so the caller can skip the write.
    assert publisher.update_cached_counts({'issues': 0}) == set()


@pytest.mark.django_db
def test_count_update_does_not_clobber_concurrent_edit(publisher):
    # A second actor edits a different column of the same row after our
    # object was loaded into memory.
    Publisher.objects.filter(pk=publisher.pk).update(name='Concurrent')

    # Our now-stale object adjusts a cached count and persists exactly the
    # fields it touched, the way _adjust_stats does.
    fields = publisher.update_cached_counts({'issues': 3})
    publisher.save(update_fields=fields)

    publisher.refresh_from_db()
    assert publisher.issue_count == 3       # count applied atomically
    assert publisher.name == 'Concurrent'   # concurrent edit NOT clobbered


@pytest.mark.django_db
def test_a_full_row_save_would_have_clobbered(publisher):
    # Demonstrates the bug the fix prevents: persisting the same F() with a
    # full-row save writes the stale name back over the concurrent edit.
    Publisher.objects.filter(pk=publisher.pk).update(name='Concurrent')

    publisher.update_cached_counts({'issues': 3})
    publisher.save()                        # the old, buggy full-row save

    publisher.refresh_from_db()
    assert publisher.issue_count == 3       # count still lands...
    assert publisher.name == 'Orig'         # ...but the concurrent edit is lost
