from django.db.models import Q, F, Count, Case, When

from apps.stats.models import CountStats
from apps.gcd.models import Series, Issue, Brand, BrandGroup
from apps.stddata.models import Language, Country


def main():
    CountStats.objects.all().delete()
    CountStats.objects.init_stats()

    for i in Language.objects.all():
        if Series.objects.filter(language=i).exists():
            CountStats.objects.init_stats(language=i)

    for i in Country.objects.all():
        if Series.objects.filter(country=i).exists():
            CountStats.objects.init_stats(country=i)

    # -------------------------------------------------------------------------
    # Rebuild Series.issue_count Caches
    # -------------------------------------------------------------------------
    # An issue contributes +1 to a Series count if:
    #   (a) It is a standard base issue (variant_of is NULL)
    #   (b) It is a cross-series variant (its series differs from its base issue's series)
    # Standard variants within the same series do not count, preventing inflation.
    #
    # This bulk aggregation MUST remain synchronized with the real-time Python
    # logic in `apps.gcd.models.issue.Issue.stat_counts()`.

    from django.db.models import Subquery, OuterRef
    from django.db.models.functions import Coalesce

    # The trailing order_by() matters: Issue's default ordering ('series',
    # 'sort_code') orders through the FK and plants a join on gcd_series in
    # the subquery's FROM clause, and MySQL refuses an UPDATE on gcd_series
    # whose subquery reads gcd_series (error 1093). Clearing the ordering
    # keeps the subquery on gcd_issue alone.
    subquery = Issue.objects.filter(
        deleted=False,
        series_id=OuterRef('pk')
    ).filter(
        Q(variant_of__isnull=True) | ~Q(series_id=F('variant_of__series_id'))
    ).values('series_id').annotate(c=Count('id')).values('c').order_by()

    Series.objects.update(issue_count=Coalesce(Subquery(subquery), 0))


    # -------------------------------------------------------------------------
    # Rebuild Brand and BrandGroup issue_count caches
    # -------------------------------------------------------------------------
    # The brand_emblem m2m counting bugs left these drifted. The counting
    # rule mirrors Issue.stat_counts()'s 'issues' key, which the cache
    # machinery maintains: distinct non-variant issues of comics
    # publications. (active_issues() alone also lists variants; that is
    # the display-side definition, not the cached one.)
    for model in (Brand, BrandGroup):
        to_update = []
        for obj in model.objects.filter(deleted=False) \
                        .only('id', 'issue_count').iterator():
            actual = obj.active_issues().filter(
                variant_of__isnull=True,
                series__is_comics_publication=True).count()
            if obj.issue_count != actual:
                obj.issue_count = actual
                to_update.append(obj)
        model.objects.bulk_update(to_update, ['issue_count'],
                                  batch_size=1000)


def run():
    main()
