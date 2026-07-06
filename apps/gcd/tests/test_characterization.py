# -*- coding: utf-8 -*-
"""
Golden-master characterization tests.

These render key pages against a small fixed object graph and compare
the HTML with committed snapshots, so refactorings can be verified to
not change behavior. Set UPDATE_SNAPSHOTS=1 to regenerate after an
intended change and commit the diff.
"""

import os
import re

import pytest
from django.urls import reverse

from apps.stddata.models import Country, Language
from apps.gcd.models import Publisher, Series, Issue

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), 'snapshots')


def _normalize(html):
    html = re.sub(
        r'name="csrfmiddlewaretoken" value="[^"]*"',
        'name="csrfmiddlewaretoken" value="NORMALIZED"', html)
    return html


def _check_snapshot(client, name, url):
    response = client.get(url)
    assert response.status_code == 200
    html = _normalize(response.content.decode())

    path = os.path.join(SNAPSHOT_DIR, '%s.html' % name)
    if os.environ.get('UPDATE_SNAPSHOTS') or not os.path.exists(path):
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        with open(path, 'w') as f:
            f.write(html)
        return
    with open(path) as f:
        expected = f.read()
    assert html == expected, (
        'Snapshot mismatch for "%s". If the change is intended, rerun '
        'with UPDATE_SNAPSHOTS=1 and commit the new snapshot.' % name)


@pytest.fixture
def page_data(db):
    # Fixed primary keys keep URLs and links inside the rendered pages
    # stable across runs.
    country = Country.objects.get_or_create(
        id=901, defaults={'code': 'zc', 'name': 'Charland'})[0]
    language = Language.objects.get_or_create(
        id=901, defaults={'code': 'zc', 'name': 'Charspeak'})[0]
    publisher = Publisher.objects.create(
        id=901, name='Characterization Publisher', country=country,
        year_began=1950, url='https://publisher.example')
    series = Series.objects.create(
        id=901, name='Characterization Series',
        sort_name='Characterization Series', year_began=1950,
        country=country, language=language, publisher=publisher,
        is_comics_publication=True, has_gallery=False,
        publication_dates='1950 - present')
    issue = Issue.objects.create(
        id=901, number='1', series=series, sort_code=0,
        publication_date='January 1950', key_date='1950-01-00')
    series.first_issue = issue
    series.last_issue = issue
    series.issue_count = 1
    series.save()
    publisher.series_count = 1
    publisher.issue_count = 1
    publisher.save()
    return publisher, series, issue


@pytest.mark.django_db
def test_publisher_page(client, page_data):
    publisher, series, issue = page_data
    _check_snapshot(client, 'publisher', reverse(
        'show_publisher', kwargs={'publisher_id': publisher.id}))


@pytest.mark.django_db
def test_series_page(client, page_data):
    publisher, series, issue = page_data
    _check_snapshot(client, 'series', reverse(
        'show_series', kwargs={'series_id': series.id}))


@pytest.mark.django_db
def test_issue_page(client, page_data):
    publisher, series, issue = page_data
    _check_snapshot(client, 'issue', reverse(
        'show_issue', kwargs={'issue_id': issue.id}))
