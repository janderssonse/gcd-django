# -*- coding: utf-8 -*-
"""
Default Meta.ordering that names a relation makes Django join the
related table into every ordered queryset of the model -- and into the
FROM clause of a grouped Subquery, which MySQL rejects for an UPDATE on
the joined table (see scripts/reset_stats.py, error 1093). On the hot
tables that is a standing tax: Issue used to pull gcd_series into every
issue queryset via ordering = ['series', ...], and Cover pulled both
gcd_issue and gcd_series. These pin the hot models join-free and make
new relation-traversing default orderings a deliberate decision.
"""

from django.apps import apps as django_apps

from apps.gcd.models import Cover, Issue

# Models whose default ordering deliberately traverses a relation (small
# tables where the join is cheap and the display order semantic), plus
# multi-table-inheritance children whose parent join is structural.
# Adding a model here must be a conscious decision, not an accident.
ORDERING_JOIN_ALLOWED = {
    'gcd.BiblioEntry',
    'gcd.BrandUse',
    'gcd.CharacterNameDetail',
    'gcd.CharacterRelation',
    'gcd.CreatorNameDetail',
    'gcd.CreatorRelation',
    'gcd.CreatorSchool',
    'gcd.CreatorSignature',
    'gcd.ExternalLink',
    'gcd.Feature',
    'gcd.FeatureRelation',
    'gcd.GroupMembership',
    'gcd.GroupNameDetail',
    'gcd.GroupRelation',
    'gcd.StoryArc',
    'gcd.StoryArcRelation',
    'gcd.StoryCharacter',
    'gcd.StoryGroup',
    'gcd.Universe',
    'oi.BiblioEntryRevision',
    'oi.CharacterRelationRevision',
    'oi.CreatorNameDetailRevision',
    'oi.CreatorRelationRevision',
    'oi.CreatorSignatureRevision',
    'oi.FeatureRelationRevision',
    'oi.GroupRelationRevision',
    'oi.IssueCreditRevision',
    'oi.PreviewCreatorSchool',
    'oi.PreviewUniverse',
    'oi.StoryArcRelationRevision',
    'oi.StoryCharacterRevision',
    'oi.StoryCreditRevision',
    'oi.StoryGroupRevision',
}


def _ordering_join_models():
    found = set()
    for model in django_apps.get_models():
        if model._meta.app_label not in ('gcd', 'oi'):
            continue
        if not model._meta.ordering:
            continue
        sql = str(model._meta.default_manager.all().query)
        if ' JOIN ' in sql:
            found.add('%s.%s' % (model._meta.app_label, model.__name__))
    return found


def test_issue_and_cover_default_querysets_are_join_free():
    for model in (Issue, Cover):
        assert ' JOIN ' not in str(model.objects.all().query)


def test_relation_traversing_default_orderings_are_deliberate():
    assert _ordering_join_models() == ORDERING_JOIN_ALLOWED
