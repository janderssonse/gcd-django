"""Feature revision cluster (roadmap C1): feature, feature-logo and feature-relation revisions. Base classes and helpers come from apps.oi.models.base; re-exported through the package __init__ so the historical import surface is unchanged."""

import itertools
import operator
import re
import calendar
import os
import glob
from datetime import timedelta

from django import forms
from django.conf import settings
from django.db import models, transaction, IntegrityError
from django.db.models import F, Manager
from django.db.models.fields import Field, related
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, \
                                               GenericRelation
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as esc
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError, FieldDoesNotExist

from imagekit.cachefiles.backends import CacheFileState
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from taggit.managers import TaggableManager

from functools import reduce

from apps.oi import states, relpath

from apps.stddata.models import Country, Language, Date, Script
from apps.stats.models import RecentIndexedIssue, CountStats

from apps.gcd.models import (
    Publisher, IndiciaPublisher, BrandGroup, Brand, BrandUse, Series,
    SeriesBond, Cover, Image, Issue, IssueCredit, PublisherCodeNumber,
    CodeNumberType, Story, StoryCredit, StoryCharacter, CharacterRole,
    StoryGroup, StoryArc, StoryArcRelation, Universe, Multiverse,
    CharacterOrderType, CharacterOrder,
    BiblioEntry, Reprint,
    SeriesPublicationType, SeriesBondType, StoryType, CreditType, FeatureType,
    Feature, FeatureLogo, FeatureRelation, Character, CharacterRelation,
    CharacterNameDetail, Group, GroupNameDetail, GroupRelation,
    GroupMembership, ImageType, Printer, IndiciaPrinter,
    Creator, CreatorArtInfluence, CreatorDegree, CreatorMembership,
    CreatorNameDetail, CreatorNonComicWork, CreatorSchool, CreatorRelation,
    CreatorSignature, NonComicWorkYear, Award, ReceivedAward, DataSource,
    ExternalLink, STORY_TYPES, CREDIT_TYPES, VCS_Codes)

from apps.gcd.models.gcddata import GcdData, GcdLink

from apps.gcd.models.issue import issue_descriptor
from apps.gcd.models.story import show_feature, show_feature_as_text, \
                                  show_characters, show_title, \
                                  _get_civilian_identity
from apps.gcd.models.image import CropToFace
from apps.indexer.views import ErrorWithMessage

from apps.oi.models.base import (
    ChangeType, CTYPES, CTYPES_INLINE, CTYPES_BULK,
    ACTION_ADD, ACTION_DELETE, ACTION_MODIFY,
    IMP_BONUS_ADD, IMP_COVER_VALUE, IMP_IMAGE_VALUE,
    IMP_APPROVER_VALUE, IMP_DELETE,
    update_count, set_series_first_last, validated_isbn,
    remove_leading_article, on_sale_date_as_string, on_sale_date_fields,
    get_keywords, save_keywords, _check_year, _imps_for_years,
    _get_revision_lock, _free_revision_lock,
    _removed_related_objects, _process_formset,
    Changeset, ChangesetComment, RevisionLock, RevisionManager,
    RevisionQuerySet, Revision, OngoingReservation, ExternalLinkRevision)

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


class FeatureRevision(Revision):
    class Meta:
        db_table = 'oi_feature_revision'
        ordering = ['-created', '-id']

    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, null=True,
                                related_name='revisions')

    name = models.CharField(max_length=255)
    leading_article = models.BooleanField(default=False)
    disambiguation = models.CharField(
      max_length=255, default='', db_index=True, blank=True,
      help_text='If needed a short phrase for the disambiguation of features '
                'with a similar or identical name.')
    genre = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    feature_type = models.ForeignKey(FeatureType, on_delete=models.CASCADE)
    year_first_published = models.IntegerField(db_index=True, blank=True,
                                               null=True)
    year_first_published_uncertain = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    keywords = models.TextField(blank=True, default='')

    external_link_revisions = GenericRelation(ExternalLinkRevision)

    source_name = 'feature'
    source_class = Feature

    @property
    def source(self):
        return self.feature

    @source.setter
    def source(self, value):
        self.feature = value

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        if fork is False:
            self.leading_article = self.feature.name != self.feature.sort_name

    def _post_assign_fields(self, changes):
        if self.leading_article:
            self.feature.sort_name = remove_leading_article(self.name)
        else:
            self.feature.sort_name = self.name

    def extra_forms(self, request):
        external_link_formset = self._create_external_link_formset(request)
        return {'external_link_formset': external_link_formset}

    def process_extra_forms(self, extra_forms):
        self._process_external_link_formset(extra_forms)

    def get_absolute_url(self):
        if self.feature is None:
            return "/feature/revision/%i/preview" % self.id
        return self.feature.get_absolute_url()

    def __str__(self):
        return '%s' % (self.name)

    ######################################
    # TODO old methods, t.b.c

    _base_field_list = ['name', 'leading_article', 'disambiguation',
                        'genre', 'language', 'feature_type',
                        'year_first_published',
                        'year_first_published_uncertain',
                        'notes', 'keywords']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'name': '',
            'leading_article': False,
            'disambiguation': '',
            'genre': '',
            'language': None,
            'feature_type': None,
            'year_first_published': None,
            'year_first_published_uncertain': False,
            'notes': '',
            'keywords': '',
        }

    def _start_imp_sum(self):
        self._seen_year_first_published = False

    def _imps_for(self, field_name):
        if field_name in ('year_first_published',
                          'year_first_published_uncertain'):
            if not self._seen_year_first_published:
                self._seen_year_first_published = True
                return 1
        elif field_name in self._field_list():
            return 1
        return 0

    def _queue_name(self):
        return '%s (%s, %s)' % (self.name, self.year_first_published,
                                self.language.code.upper())


class FeatureLogoRevision(Revision):
    class Meta:
        db_table = 'oi_feature_logo_revision'
        ordering = ['-created', '-id']

    feature = models.ManyToManyField(Feature, related_name='logo_revisions')
    feature_logo = models.ForeignKey(FeatureLogo, on_delete=models.CASCADE,
                                     null=True, related_name='revisions')

    name = models.CharField(max_length=255)
    leading_article = models.BooleanField(default=False)
    generic = models.BooleanField(default=False)
    year_began = models.IntegerField(db_index=True, null=True, blank=True)
    year_ended = models.IntegerField(null=True, blank=True)
    year_began_uncertain = models.BooleanField(default=False)
    year_ended_uncertain = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    image_revision = models.ForeignKey('oi.ImageRevision',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       related_name='feature_logo_revisions')

    source_name = 'feature_logo'
    source_class = FeatureLogo

    @property
    def source(self):
        return self.feature_logo

    @source.setter
    def source(self, value):
        self.feature_logo = value

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        if fork is False:
            self.leading_article = (self.feature_logo.name !=
                                    self.feature_logo.sort_name)

    def _post_assign_fields(self, changes):
        if self.leading_article:
            self.feature_logo.sort_name = remove_leading_article(self.name)
        else:
            self.feature_logo.sort_name = self.name

    def _handle_dependents(self, changes):
        self._handle_dependent_image_revision()

    def get_absolute_url(self):
        if self.feature_logo is None:
            return "/feature_logo/revision/%i/preview" % self.id
        return self.feature_logo.get_absolute_url()

    def full_name(self):
        return self.__str__()

    def __str__(self):
        return '%s' % (self.name)

    ######################################
    # TODO old methods, t.b.c

    _base_field_list = ['name', 'leading_article', 'feature', 'generic',
                        'year_began', 'year_began_uncertain', 'year_ended',
                        'year_ended_uncertain', 'notes']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'feature': None,
            'name': '',
            'leading_article': False,
            'generic': False,
            'year_began': None,
            'year_ended': None,
            'year_began_uncertain': False,
            'year_ended_uncertain': False,
            'notes': '',
        }

    def _start_imp_sum(self):
        self._seen_year_began = False
        self._seen_year_ended = False

    def _imps_for(self, field_name):
        years_found, value = _imps_for_years(self, field_name,
                                             'year_began', 'year_ended')
        if years_found:
            return value
        elif field_name in self._base_field_list:
            return 1
        return 0

    def _queue_name(self):
        return '%s (%s)' % (self.name, self.year_began)


class FeatureRelationRevision(Revision):
    """
    Relations between features.
    """

    class Meta:
        db_table = 'oi_feature_relation_revision'
        ordering = ('to_feature', 'relation_type', 'from_feature')
        verbose_name_plural = 'Feature Relation Revisions'

    feature_relation = models.ForeignKey('gcd.FeatureRelation',
                                         on_delete=models.CASCADE,
                                         null=True,
                                         related_name='revisions')

    to_feature = models.ForeignKey('gcd.Feature',
                                   on_delete=models.CASCADE,
                                   related_name='to_feature_revisions')
    relation_type = models.ForeignKey('gcd.FeatureRelationType',
                                      on_delete=models.CASCADE,
                                      related_name='revisions')
    from_feature = models.ForeignKey('gcd.Feature',
                                     on_delete=models.CASCADE,
                                     related_name='from_feature_revisions')
    notes = models.TextField(blank=True)

    _base_field_list = ['from_feature', 'relation_type', 'to_feature', 'notes']

    def _field_list(self):
        field_list = self._base_field_list
        return field_list

    def _get_blank_values(self):
        return {
            'from_feature': None,
            'to_feature': None,
            'relation_type': None,
            'notes': ''
        }

    source_name = 'feature_relation'
    source_class = FeatureRelation

    @property
    def source(self):
        return self.feature_relation

    @source.setter
    def source(self, value):
        self.feature_relation = value

    def _get_source(self):
        return self.feature_relation

    def _get_source_name(self):
        return 'feature_relation'

    def _imps_for(self, field_name):
        return 1

    def _pre_delete(self, changes):
        for revision in self.source.revisions.all():
            setattr(revision, 'feature_relation_id', None)
            revision.save()
        self.feature_relation_id = None

    def __str__(self):
        return '%s >%s< %s' % (str(self.from_feature),
                               str(self.relation_type),
                               str(self.to_feature)
                               )


