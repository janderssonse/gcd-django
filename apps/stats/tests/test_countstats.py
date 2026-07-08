# -*- coding: utf-8 -*-



from unittest import mock
import pytest

from apps.stddata.models import Country, Language
from apps.stats.models import CountStats, CountStatsManager
from apps.gcd.models.issue import INDEXED


ANY_LANGUAGE = Language(id=1, code='XZZ', name='Test Language')
ANY_COUNTRY = Country(id=1, code='XYY', name='Test Country')

PUB_COUNT = 1
CREATOR_COUNT = 2
SERIES_COUNT = 4
INDEX_COUNT = 5
VARIANT_COUNT = 6
ISSUE_COUNT = 7
COVER_COUNT = 8
STORY_COUNT = 9


def test_init_stats_not_both():
    with pytest.raises(ValueError) as excinfo:
        CountStats.objects.init_stats(language=ANY_LANGUAGE,
                                      country=ANY_COUNTRY)
    assert 'either country or language stats' in str(excinfo.value)


@pytest.fixture
def patched_filters():
    """
    Returns all of the *.objects.filter/create methods patched as a tuple.

    Order:  CountStat.create, CountStat.filter, Publisher, Creator,
            Series, Issue, Cover, Story
    """
    p = 'apps.stats.models'

    # Note:  As single letters, "Series" is always s, "Story" is always t.
    with mock.patch('%s.CountStatsManager.filter' % p) as cs_filter, \
            mock.patch('%s.CountStatsManager.create' % p) as cs_create, \
            mock.patch('%s.Story.objects.filter' % p) as t_filter, \
            mock.patch('%s.Cover.objects.filter' % p) as c_filter, \
            mock.patch('%s.Issue.objects.filter' % p) as i_filter, \
            mock.patch('%s.Series.objects.filter' % p) as s_filter, \
            mock.patch('%s.Creator.objects.filter' % p) as cr_filter, \
            mock.patch('%s.Publisher.objects.filter' % p) as p_filter:

        p_filter.return_value.count.return_value = PUB_COUNT
        cr_filter.return_value.count.return_value = CREATOR_COUNT
        s_filter.return_value.count.return_value = SERIES_COUNT
        i_filter.return_value.count.return_value = ISSUE_COUNT
        i_filter.return_value.exclude.return_value.count.return_value = \
            VARIANT_COUNT
        i_filter.return_value.filter.return_value.count.return_value = \
            INDEX_COUNT
        c_filter.return_value.count.return_value = COVER_COUNT
        t_filter.return_value.count.return_value = STORY_COUNT

        yield (cs_create, cs_filter, p_filter, cr_filter, s_filter, i_filter,
               c_filter, t_filter)


def _make_init_stats_kwargs(language=None, country=None):
        kwargs = {'deleted': False}
        if country is not None:
            kwargs['country'] = country

        p_b_ip_kwargs = kwargs.copy()

        if language is not None:
            kwargs['language'] = language

        s_kwargs = kwargs.copy()
        s_kwargs['is_comics_publication'] = True

        i_kwargs = {k if k == 'deleted' else 'series__%s' % k: v
                    for k, v in s_kwargs.items()}
        c_t_kwargs = {k if k == 'deleted' else 'issue__series__%s' % k: v
                      for k, v in s_kwargs.items()
                      if k != 'is_comics_publication'}

        return p_b_ip_kwargs, s_kwargs, i_kwargs, c_t_kwargs


def test_init_stats_language(patched_filters):
        (cs_create, cs_filter, p_filter, cr_filter, s_filter, i_filter,
         c_filter, t_filter) = patched_filters

        (p_b_ip_kwargs, s_kwargs, i_kwargs,
         c_t_kwargs) = _make_init_stats_kwargs(language=ANY_LANGUAGE)

        CountStats.objects.init_stats(language=ANY_LANGUAGE)

        cs_filter.assert_called_once_with(language=ANY_LANGUAGE, country=None)
        cs_filter.return_value.delete.assert_called_once_with()
        s_filter.assert_called_once_with(**s_kwargs)

        i_filter.assert_has_calls([
            mock.call(variant_of=None, **i_kwargs),
            mock.call().count(),
            mock.call(**i_kwargs),
            mock.call().exclude(variant_of=None),
            mock.call().exclude().count(),
            mock.call(variant_of=None, **i_kwargs),
            mock.call().filter(is_indexed__gt=INDEXED['some_data']),
            mock.call().filter().count()])

        c_filter.assert_called_once_with(**c_t_kwargs)
        t_filter.assert_called_once_with(**c_t_kwargs)

        lc_args = {'language': ANY_LANGUAGE, 'country': None}
        cs_create.assert_has_calls([
            mock.call(name='series', count=SERIES_COUNT, **lc_args),
            mock.call(name='issues', count=ISSUE_COUNT, **lc_args),
            mock.call(name='variant issues', count=VARIANT_COUNT, **lc_args),
            mock.call(name='issue indexes', count=INDEX_COUNT, **lc_args),
            mock.call(name='covers', count=COVER_COUNT, **lc_args),
            mock.call(name='stories', count=STORY_COUNT, **lc_args)])


def test_init_stats_country(patched_filters):
        (cs_create, cs_filter, p_filter, cr_filter, s_filter, i_filter,
         c_filter, t_filter) = patched_filters

        (p_b_ip_kwargs, s_kwargs, i_kwargs,
         c_t_kwargs) = _make_init_stats_kwargs(country=ANY_COUNTRY)

        CountStats.objects.init_stats(country=ANY_COUNTRY)

        cs_filter.assert_called_once_with(language=None, country=ANY_COUNTRY)
        cs_filter.return_value.delete.assert_called_once_with()

        p_filter.assert_called_once_with(**p_b_ip_kwargs)
        s_filter.assert_called_once_with(**s_kwargs)

        i_filter.assert_has_calls([
            mock.call(variant_of=None, **i_kwargs),
            mock.call().count(),
            mock.call(**i_kwargs),
            mock.call().exclude(variant_of=None),
            mock.call().exclude().count(),
            mock.call(variant_of=None, **i_kwargs),
            mock.call().filter(is_indexed__gt=INDEXED['some_data']),
            mock.call().filter().count()])

        c_filter.assert_called_once_with(**c_t_kwargs)
        t_filter.assert_called_once_with(**c_t_kwargs)

        # Publishers don't pass language, not even a None value.
        c_args = {'country': ANY_COUNTRY}
        lc_args = {'language': None, 'country': ANY_COUNTRY}
        cs_create.assert_has_calls([
            mock.call(name='publishers', count=PUB_COUNT, **c_args),
            mock.call(name='series', count=SERIES_COUNT, **lc_args),
            mock.call(name='issues', count=ISSUE_COUNT, **lc_args),
            mock.call(name='variant issues', count=VARIANT_COUNT, **lc_args),
            mock.call(name='issue indexes', count=INDEX_COUNT, **lc_args),
            mock.call(name='covers', count=COVER_COUNT, **lc_args),
            mock.call(name='stories', count=STORY_COUNT, **lc_args)])


def test_init_stats_neither(patched_filters):
        (cs_create, cs_filter, p_filter, cr_filter, s_filter, i_filter,
         c_filter, t_filter) = patched_filters

        (p_b_ip_kwargs, s_kwargs, i_kwargs,
         c_t_kwargs) = _make_init_stats_kwargs()

        CountStats.objects.init_stats()

        cs_filter.assert_called_once_with(language=None, country=None)
        cs_filter.return_value.delete.assert_called_once_with()

        p_filter.assert_called_once_with(**p_b_ip_kwargs)
        cr_filter.assert_called_once_with(**p_b_ip_kwargs)
        s_filter.assert_called_once_with(**s_kwargs)

        i_filter.assert_has_calls([
            mock.call(variant_of=None, **i_kwargs),
            mock.call().count(),
            mock.call(**i_kwargs),
            mock.call().exclude(variant_of=None),
            mock.call().exclude().count(),
            mock.call(variant_of=None, **i_kwargs),
            mock.call().filter(is_indexed__gt=INDEXED['some_data']),
            mock.call().filter().count()])

        c_filter.assert_called_once_with(**c_t_kwargs)
        t_filter.assert_called_once_with(**c_t_kwargs)

        # Publishers don't pass language, not even a None value.
        # Brands don't pass either.
        c_args = {'country': None}
        lc_args = {'language': None, 'country': None}
        cs_create.assert_has_calls([
            mock.call(name='publishers', count=PUB_COUNT, **c_args),
            mock.call(name='creators', count=CREATOR_COUNT),
            mock.call(name='series', count=SERIES_COUNT, **lc_args),
            mock.call(name='issues', count=ISSUE_COUNT, **lc_args),
            mock.call(name='variant issues', count=VARIANT_COUNT, **lc_args),
            mock.call(name='issue indexes', count=INDEX_COUNT, **lc_args),
            mock.call(name='covers', count=COVER_COUNT, **lc_args),
            mock.call(name='stories', count=STORY_COUNT, **lc_args)])


# update_count is now a single atomic UPDATE per statistic, so these assert
# on the resulting database state rather than on get()/save() call chains.

@pytest.mark.django_db
def test_update_count_generic_only():
    CountStats.objects.create(name='foo', count=10)
    CountStats.objects.update_count('foo', 3)
    assert CountStats.objects.get(name='foo', language=None,
                                  country=None).count == 13


@pytest.mark.django_db
def test_update_count_negative_delta():
    CountStats.objects.create(name='foo', count=10)
    CountStats.objects.update_count('foo', -4)
    assert CountStats.objects.get(name='foo', language=None,
                                  country=None).count == 6


@pytest.mark.django_db
def test_update_count_language_and_country():
    language = Language.objects.create(code='xu', name='UT Language')
    country = Country.objects.create(code='xv', name='UT Country')
    CountStats.objects.create(name='foo', count=10)
    CountStats.objects.create(name='foo', language=language, count=5)
    CountStats.objects.create(name='foo', country=country, count=2)

    CountStats.objects.update_count('foo', 3, language=language,
                                    country=country)

    assert CountStats.objects.get(name='foo', language=None,
                                  country=None).count == 13
    assert CountStats.objects.get(name='foo', language=language,
                                  country=None).count == 8
    assert CountStats.objects.get(name='foo', language=None,
                                  country=country).count == 5


@pytest.mark.django_db
def test_update_count_inits_missing_language_stat():
    # The generic stat exists, but there is no language stat for this field
    # yet, so the whole language set is initialized instead of updated.
    language = Language.objects.create(code='xu', name='UT Language')
    CountStats.objects.create(name='foo', count=10)

    with mock.patch.object(CountStatsManager, 'init_stats') as is_mock:
        CountStats.objects.update_count('foo', 3, language=language)

    is_mock.assert_called_once_with(language=language)
    assert CountStats.objects.get(name='foo', language=None,
                                  country=None).count == 13


@pytest.mark.django_db
def test_update_count_inits_missing_country_stat():
    country = Country.objects.create(code='xv', name='UT Country')
    CountStats.objects.create(name='foo', count=10)

    with mock.patch.object(CountStatsManager, 'init_stats') as is_mock:
        CountStats.objects.update_count('foo', 3, country=country)

    is_mock.assert_called_once_with(country=country)
    assert CountStats.objects.get(name='foo', language=None,
                                  country=None).count == 13


@pytest.fixture
def mocks_for_update_all():
    """
    Returns a 3-tuple of mocks for testing update_all().

    In order (on CountStatsManager): filter, init_stats, update_count
        * CountStatsManager.
    """
    path = 'apps.stats.models.CountStatsManager'
    with mock.patch('%s.filter' % path) as filter_mock, \
            mock.patch('%s.init_stats' % path) as is_mock, \
            mock.patch('%s.update_count' % path) as uc_mock:

        yield filter_mock, is_mock, uc_mock


def test_update_all_language_only(mocks_for_update_all):
    filter_mock, is_mock, uc_mock = mocks_for_update_all

    CountStats.objects.update_all_counts(
        # Note that 'series issues' is special and should be ignored.
        # It is used by Series in local cached counts, but CountStats
        # will sometimes see it.  We only need to test this in one
        # case, arbitrarily choosing this one (language_only).
        {'foo': 1, 'bar': 5, 'series issues': 100}, language=ANY_LANGUAGE)

    assert is_mock.called is False
    filter_mock.assert_called_once_with(language=ANY_LANGUAGE, country=None)
    filter_mock.return_value.exists.assert_called_once_with()

    uc_mock.assert_has_calls([
        mock.call(field='foo', delta=1, language=ANY_LANGUAGE, country=None),
        mock.call(field='bar', delta=5, language=ANY_LANGUAGE, country=None),
    ])
    assert uc_mock.call_count == 2


def test_update_all_country_only(mocks_for_update_all):
    filter_mock, is_mock, uc_mock = mocks_for_update_all

    CountStats.objects.update_all_counts(
        {'foo': 1, 'bar': 5}, country=ANY_COUNTRY)

    assert is_mock.called is False
    filter_mock.assert_called_once_with(language=None, country=ANY_COUNTRY)
    filter_mock.return_value.exists.assert_called_once_with()

    uc_mock.assert_has_calls([
        mock.call(field='foo', delta=1, language=None, country=ANY_COUNTRY),
        mock.call(field='bar', delta=5, language=None, country=ANY_COUNTRY),
    ])
    assert uc_mock.call_count == 2


def test_update_all_init_both(mocks_for_update_all):
    filter_mock, is_mock, uc_mock = mocks_for_update_all

    filter_mock.return_value.exists.return_value = False

    CountStats.objects.update_all_counts(
        {'foo': 1, 'bar': 5}, country=ANY_COUNTRY, language=ANY_LANGUAGE)

    filter_mock.assert_has_calls([mock.call(country=ANY_COUNTRY,
                                            language=None),
                                  mock.call(country=None,
                                            language=ANY_LANGUAGE)],
                                 any_order=True)
    assert filter_mock.call_count == 2

    is_mock.assert_has_calls([mock.call(country=ANY_COUNTRY),
                              mock.call(language=ANY_LANGUAGE)],
                             any_order=True)
    assert is_mock.call_count == 2

    uc_mock.assert_has_calls([
        mock.call(field='foo', delta=1, language=None, country=None),
        mock.call(field='bar', delta=5, language=None, country=None),
    ])
    assert uc_mock.call_count == 2


def test_update_all_negate(mocks_for_update_all):
    filter_mock, is_mock, uc_mock = mocks_for_update_all

    CountStats.objects.update_all_counts({'foo': 1, 'bar': 5},
                                         negate=True,
                                         country=ANY_COUNTRY,
                                         language=ANY_LANGUAGE)

    filter_mock.assert_has_calls([mock.call(country=ANY_COUNTRY,
                                            language=None),
                                  mock.call(country=None,
                                            language=ANY_LANGUAGE)],
                                 any_order=True)
    assert filter_mock.call_count == 2

    assert not is_mock.called

    uc_mock.assert_has_calls([
        mock.call(field='foo', delta=-1,
                  language=ANY_LANGUAGE, country=ANY_COUNTRY),
        mock.call(field='bar', delta=-5,
                  language=ANY_LANGUAGE, country=ANY_COUNTRY)])
    assert uc_mock.call_count == 2
