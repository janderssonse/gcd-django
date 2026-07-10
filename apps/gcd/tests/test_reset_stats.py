# -*- coding: utf-8 -*-
"""
reset_stats rebuilds the cached statistics from the display tables. The
Series.issue_count rebuild runs an UPDATE on gcd_series driven by a
subquery; Issue's default ordering used to leak a join on gcd_series
into that subquery, which MySQL rejects (error 1093). These run the
rebuild for real and pin the variant counting rules.
"""

import pytest

from apps.gcd.models import Publisher, Series, Issue, Brand, BrandGroup
from apps.stats.models import CountStats
from apps.stddata.models import Country, Language
from scripts.reset_stats import main


@pytest.fixture
def two_series(db):
    country, _ = Country.objects.get_or_create(
        code='zz', defaults={'name': 'Zedland'})
    language, _ = Language.objects.get_or_create(
        code='zz', defaults={'name': 'Zedish'})
    publisher = Publisher.objects.create(
        name='Stats Publishing', country=country, year_began=1990)

    def series(name):
        return Series.objects.create(
            name=name, sort_name=name, year_began=1990, country=country,
            language=language, publisher=publisher,
            is_comics_publication=True, has_gallery=False)

    return series('Alpha'), series('Beta')


def _issue(series, sort_code, **kwargs):
    return Issue.objects.create(
        number=str(sort_code), series=series, sort_code=sort_code,
        **kwargs)


@pytest.mark.django_db
def test_rebuild_counts_base_and_cross_series_variants(two_series):
    alpha, beta = two_series
    base = _issue(alpha, 1)
    _issue(alpha, 2)                    # second base issue: counted
    _issue(alpha, 3, variant_of=base)   # same-series variant: not counted
    _issue(beta, 1, variant_of=base)    # cross-series variant: counted
    _issue(beta, 2, deleted=True)       # deleted: not counted

    # Corrupt the cached counts; the rebuild must repair them.
    Series.objects.update(issue_count=99)

    main()

    alpha.refresh_from_db()
    beta.refresh_from_db()
    assert alpha.issue_count == 2
    assert beta.issue_count == 1


@pytest.mark.django_db
def test_rebuild_zeroes_series_without_issues(two_series):
    alpha, _ = two_series
    Series.objects.update(issue_count=7)

    main()

    alpha.refresh_from_db()
    assert alpha.issue_count == 0
    assert CountStats.objects.exists()


@pytest.mark.django_db
def test_rebuild_brand_and_group_counts_dedup_shared_group(two_series):
    alpha, _ = two_series
    group = BrandGroup.objects.create(
        name='House Group', parent=alpha.publisher, year_began=1990)
    one = Brand.objects.create(name='Emblem One', year_began=1990)
    two = Brand.objects.create(name='Emblem Two', year_began=1990)
    one.group.set([group])
    two.group.set([group])

    issue = _issue(alpha, 1)
    issue.brand_emblem.set([one, two])
    _issue(alpha, 2, deleted=True).brand_emblem.set([one])
    # Not counted: a variant, and an issue of a non-comics publication --
    # stat_counts() sets no 'issues' delta for either.
    _issue(alpha, 3, variant_of=issue).brand_emblem.set([one])
    non_comics = Series.objects.create(
        name='Mag', sort_name='Mag', year_began=1990,
        country=alpha.country, language=alpha.language,
        publisher=alpha.publisher, is_comics_publication=False,
        has_gallery=False)
    _issue(non_comics, 1).brand_emblem.set([one])

    # Corrupt the cached counts; the rebuild must repair them, counting
    # the shared-group issue once and skipping the deleted issue.
    Brand.objects.update(issue_count=99)
    BrandGroup.objects.update(issue_count=99)

    main()

    group.refresh_from_db()
    one.refresh_from_db()
    two.refresh_from_db()
    assert group.issue_count == 1
    assert one.issue_count == 1
    assert two.issue_count == 1
