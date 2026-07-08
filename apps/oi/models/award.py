"""Award revision cluster (roadmap C1): award and received-award revisions plus PreviewReceivedAward. Base classes and helpers come from apps.oi.models.base; re-exported through the package __init__ so the historical import surface is unchanged."""

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


class AwardRevision(Revision):
    """
    record the different comic awards
    """

    class Meta:
        db_table = 'oi_award_revision'
        ordering = ['created', '-id']
        verbose_name_plural = 'Award Revisions'

    award = models.ForeignKey('gcd.Award', on_delete=models.CASCADE,
                              null=True, related_name='revisions')
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    source_name = 'award'
    source_class = Award

    @property
    def source(self):
        return self.award

    @source.setter
    def source(self, value):
        self.award = value

    def get_absolute_url(self):
        if self.award is None:
            return "/award/revision/%i/preview" % self.id
        return self.award.get_absolute_url()

    def __str__(self):
        return self.name

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['name',
                        'notes',
                        ]

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'name': '',
            'notes': '',
        }

    def _imps_for(self, field_name):
        if field_name in self._base_field_list:
            return 1
        return 0


class ReceivedAwardRevision(Revision):
    class Meta:
        db_table = 'oi_received_award_revision'
        ordering = ['created', '-id']
        verbose_name_plural = 'Received Award Revisions'

    received_award = models.ForeignKey('gcd.ReceivedAward',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       related_name='revisions')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    recipient = GenericForeignKey('content_type', 'object_id')

    award = models.ForeignKey(Award, on_delete=models.CASCADE,
                              null=True, blank=True)
    award_name = models.CharField(max_length=255, blank=True)
    no_award_name = models.BooleanField(default=False)
    award_year = models.PositiveSmallIntegerField(null=True, blank=True)
    award_year_uncertain = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    source_name = 'received_award'
    source_class = ReceivedAward

    @property
    def source(self):
        return self.received_award

    @source.setter
    def source(self, value):
        self.received_award = value

    def _do_complete_added_revision(self, recipient=None, award=None):
        self.recipient = recipient
        self.award = award

    def _do_create_dependent_revisions(self, delete=False):
        from apps.oi.models import reserve_data_sources
        data_sources = self.received_award.data_source.all()
        reserve_data_sources(data_sources, self.changeset, self, delete)

    def get_absolute_url(self):
        if self.received_award is None:
            return "/received_award/revision/%i/preview" % self.id
        return self.received_award.get_absolute_url()

    def __str__(self):
        if self.award:
            name = '%s - %s' % (self.award.name, self.award_name)
        else:
            name = '%s' % (self.award_name)
        if self.award_year:
            return '%s: %s (%d)' % (self.recipient, name, self.award_year)
        else:
            return '%s: %s' % (self.recipient, name)

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['award',
                        'award_name',
                        'no_award_name',
                        'award_year',
                        'award_year_uncertain',
                        'notes',
                        ]

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'award': '',
            'award_name': '',
            'no_award_name': False,
            'award_year': None,
            'award_year_uncertain': False,
            'notes': '',
        }

    def _start_imp_sum(self):
        self._seen_year = False
        self._seen_award_name = False

    def _imps_for(self, field_name):
        if field_name in ('award_year',
                          'award_year_uncertain'):
            if not self._seen_year:
                self._seen_year = True
                return 1
        elif field_name in ('award_name',
                            'no_award_name'):
            if not self._seen_award_name:
                self._seen_award_name = True
                return 1
        elif field_name in self._base_field_list:
            return 1
        return 0


class PreviewReceivedAward(ReceivedAward):
    class Meta:
        proxy = True

    @property
    def data_source(self):
        from apps.oi.models import DataSourceRevision
        return DataSourceRevision.objects.filter(
          revision_id=self.revision.id,
          content_type=ContentType.objects.get_for_model(self.revision))


