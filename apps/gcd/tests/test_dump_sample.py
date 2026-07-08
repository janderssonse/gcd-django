# -*- coding: utf-8 -*-
"""
Real-data verification lane (roadmap A4).

These run against the committed subset extracted from a comics.org dump
(see dumps/README.md via `just dump-extract`), so they exercise real-shaped
data -- deep credit graphs, real value quirks -- that the synthetic
sample_data graph does not. Marked `dump`; run with `just test-dump`
(excluded from the default suite, which needs no dump).
"""

import pytest
from django.core.management import call_command

from apps.gcd.models import Series, Issue, Story, StoryCredit

FIXTURE = 'apps/gcd/tests/fixtures/dump_sample.json'


@pytest.fixture
def dump_data(db):
    call_command('loaddata', FIXTURE)


@pytest.mark.dump
def test_dump_fixture_loads(dump_data):
    # The fixture is a FK-closed subset; if the closure missed a reference
    # loaddata would fail before we get here.
    assert Series.objects.exists()
    assert Issue.objects.exists()
    assert Story.objects.exists()
    assert StoryCredit.objects.exists()


@pytest.mark.dump
def test_dump_credits_reference_real_creators(dump_data):
    # Referential integrity real data must satisfy: every story credit points
    # to a creator name detail whose creator exists.
    credits = StoryCredit.objects.select_related('creator__creator',
                                                 'credit_type')
    assert credits.exists()
    for credit in credits:
        assert credit.creator is not None
        assert credit.creator.creator is not None
        assert credit.credit_type is not None


@pytest.mark.dump
def test_dump_issue_pages_render(client, dump_data):
    # Real issues render end to end on the public page.
    for issue in Issue.objects.all():
        response = client.get(issue.get_absolute_url())
        assert response.status_code == 200, \
            'issue %d did not render' % issue.id
