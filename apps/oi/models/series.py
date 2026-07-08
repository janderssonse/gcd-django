"""Series and series-bond revision cluster (roadmap C1). Base classes and helpers come from apps.oi.models.base; re-exported through the package __init__ so the historical import surface is unchanged."""

import itertools
import operator
import re
import calendar
import os
import glob
from stdnum import isbn
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


def get_series_field_list():
    return ['name', 'leading_article', 'imprint', 'format', 'color',
            'dimensions', 'paper_stock', 'binding', 'publishing_format',
            'publication_type', 'is_singleton', 'year_began',
            'year_began_uncertain', 'year_ended', 'year_ended_uncertain',
            'is_current', 'country', 'language', 'has_barcode',
            'has_indicia_frequency', 'has_indicia_printer', 'has_isbn',
            'has_issue_title', 'has_volume', 'has_rating',
            'has_publisher_code_number', 'is_comics_publication',
            'has_about_comics', 'tracking_notes', 'notes', 'keywords']


class SeriesRevision(Revision):
    class Meta:
        db_table = 'oi_series_revision'
        ordering = ['-created', '-id']

    series = models.ForeignKey(Series, on_delete=models.CASCADE,
                               null=True, related_name='revisions')

    # When adding a series, this requests the ongoing reservation upon
    # approval of the new series.  The request will be granted unless the
    # indexer has reached their maximum number of ongoing reservations
    # at the time of approval.
    reservation_requested = models.BooleanField(default=False)

    name = models.CharField(max_length=255)
    leading_article = models.BooleanField(default=False)

    # The "format" field is a legacy field that is being split into
    # color, dimensions, paper_stock, binding, and publishing_format
    format = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=255, blank=True)
    dimensions = models.CharField(max_length=255, blank=True)
    paper_stock = models.CharField(max_length=255, blank=True)
    binding = models.CharField(max_length=255, blank=True)
    publishing_format = models.CharField(max_length=255, blank=True)
    publication_type = models.ForeignKey(SeriesPublicationType,
                                         on_delete=models.CASCADE,
                                         null=True, blank=True)

    year_began = models.IntegerField()
    year_ended = models.IntegerField(null=True, blank=True)
    year_began_uncertain = models.BooleanField(default=False)
    year_ended_uncertain = models.BooleanField(default=False)
    is_current = models.BooleanField(default=False)

    publication_notes = models.TextField(blank=True)

    # Fields for tracking relationships between series.
    tracking_notes = models.TextField(blank=True)

    # Fields for handling the presence of certain issue fields
    has_barcode = models.BooleanField(default=False)
    has_indicia_frequency = models.BooleanField(default=False)
    has_indicia_printer = models.BooleanField(default=False)
    has_isbn = models.BooleanField(default=False)
    has_issue_title = models.BooleanField(default=False)
    has_volume = models.BooleanField(default=False)
    has_rating = models.BooleanField(default=False)
    has_about_comics = models.BooleanField(default=False)
    has_publisher_code_number = models.BooleanField(default=False)

    is_comics_publication = models.BooleanField(default=False)
    is_singleton = models.BooleanField(default=False)

    notes = models.TextField(blank=True)
    external_link_revisions = GenericRelation(ExternalLinkRevision)
    keywords = models.TextField(blank=True, default='')

    # Country and Language info.
    country = models.ForeignKey(Country, on_delete=models.CASCADE,
                                related_name='series_revisions')
    language = models.ForeignKey(Language, on_delete=models.CASCADE,
                                 related_name='series_revisions')

    # Fields related to the publishers table.
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE,
                                  related_name='series_revisions')
    # Imprint is removed from Series, but here we keep it around for the
    # change history of old revisions.
    imprint = models.ForeignKey(Publisher, on_delete=models.CASCADE,
                                null=True, blank=True, default=None,
                                related_name='imprint_series_revisions')
    date_inferred = models.BooleanField(default=False)

    source_name = 'series'
    source_class = Series

    @property
    def source(self):
        return self.series

    @source.setter
    def source(self, value):
        self.series = value

    @classmethod
    def _get_excluded_field_names(cls):
        return frozenset(
            super(SeriesRevision, cls)._get_excluded_field_names() |
            {'open_reserve', 'publication_dates'}
        )

    @classmethod
    def _get_parent_field_tuples(cls):
        return frozenset({('publisher',)})

    @classmethod
    def _get_major_flag_field_tuples(self):
        return frozenset({
            ('is_comics_publication',),
            ('is_current',),
            ('is_singleton',),
        })

    @classmethod
    def _get_deprecated_field_names(cls):
        return frozenset({'format'})

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        if fork is False:
            self.leading_article = self.series.name != self.series.sort_name

    def _do_complete_added_revision(self, publisher):
        """
        Do the necessary processing to complete the fields of a new
        series revision for adding a record before it can be saved.
        """
        self.publisher = publisher
        if self.is_singleton:
            self.year_ended = self.year_began
            self.year_ended_uncertain = self.year_began_uncertain

    def _TODO_handle_prerequisites(self, changes):
        # Handle deletion of the singleton issue before getting the
        # series stat counts to avoid double-counting the deletion.
        # TODO currently never used, has_dependents does not handle
        # singletons separately, so active_issues.count prevents joint delete
        if self.deleted and self.series.is_singleton:
            from apps.oi.models import IssueRevision
            issue_revision = IssueRevision.clone(
                instance=self.series.issue_set[0], changeset=self.changeset)
            issue_revision.deleted = True
            issue_revision.save()
            # TODO if joint delete changed, check here in regard to counting
            issue_revision.commit_to_display()

    def _post_assign_fields(self, changes):
        if self.leading_article:
            self.series.sort_name = remove_leading_article(self.name)
        else:
            self.series.sort_name = self.name

    def _pre_save_object(self, changes):
        if changes['from is_current']:
            reservation = self.series.get_ongoing_reservation()
            if reservation:
                reservation.delete()

        if changes['to is_comics_publication']:
            if not self.added:
                # TODO: But don't we count covers for some non-comics?
                self.series.has_gallery = bool(self.series.scan_count)

    def _handle_dependents(self, changes):
        # Handle adding the singleton issue last, to avoid double-counting
        # the addition in statistics.
        if changes['to is_singleton'] and self.series.issue_count == 0:
            from apps.oi.models import IssueRevision
            issue_revision = IssueRevision(
              changeset=self.changeset,
              series=self.series,
              after=None,
              number='[nn]',
              publication_date=self.year_began,
              notes=self.notes,
              keywords=self.keywords,
              reservation_requested=self.reservation_requested)
            if self.notes:
                self.notes = ''
                self.save()
                self.series.notes = ''
                self.series.save()
            # We assume that a non-four-digit year is a typo of some
            # sort, and do not propagate it.  The approval process
            # should catch that sort of thing.
            # TODO: Consider a validator on year_began?
            if len(str(self.year_began)) == 4:
                issue_revision.key_date = '%d-00-00' % self.year_began
            issue_revision.save()

    def extra_forms(self, request):
        external_link_formset = self._create_external_link_formset(request)
        return {'external_link_formset': external_link_formset}

    def process_extra_forms(self, extra_forms):
        self._process_external_link_formset(extra_forms)

    def get_absolute_url(self):
        if self.series is None:
            return "/series/revision/%i/preview" % self.id
        return self.series.get_absolute_url()

    def __str__(self):
        if self.series is None:
            return '%s (%s series)' % (self.name, self.year_began)
        return str(self.series)

    ######################################
    # TODO old methods, t.b.c

    def _field_list(self):
        fields = get_series_field_list()
        if self.previous() and (self.previous().publisher != self.publisher):
            fields = fields[0:2] + ['publisher'] + fields[2:]
        return fields + ['publication_notes']

    def _get_blank_values(self):
        return {
            'name': '',
            'leading_article': False,
            'format': '',
            'color': '',
            'dimensions': '',
            'paper_stock': '',
            'binding': '',
            'publishing_format': '',
            'publication_type': None,
            'is_singleton': False,
            'notes': '',
            'keywords': '',
            'year_began': None,
            'year_ended': None,
            'year_began_uncertain': None,
            'year_ended_uncertain': None,
            'is_current': None,
            'publication_notes': '',
            'tracking_notes': '',
            'country': None,
            'language': None,
            'publisher': None,
            'imprint': None,
            'has_barcode': True,
            'has_indicia_frequency': False,
            'has_indicia_printer': False,
            'has_isbn': True,
            'has_issue_title': False,
            'has_volume': False,
            'has_rating': False,
            'has_publisher_code_number': False,
            'has_about_comics': False,
            'is_comics_publication': True,
        }

    def _start_imp_sum(self):
        self._seen_year_began = False
        self._seen_year_ended = False

    def _imps_for(self, field_name):
        years_found, value = _imps_for_years(self, field_name,
                                             'year_began', 'year_ended')
        if years_found:
            return value
        return 1


class SeriesBondRevisionManager(RevisionManager):

    def clone_revision(self, series_bond, changeset):
        """
        Create a new revision based on a SeriesBond instance.

        This new revision will be where the edits are made.
        """
        return RevisionManager._clone_revision(self,
                                               instance=series_bond,
                                               instance_class=SeriesBond,
                                               changeset=changeset)

    def _do_create_revision(self, series_bond, changeset):
        """
        Helper delegate to do the class-specific work of clone_revision.
        """
        revision = SeriesBondRevision(
            # revision-specific fields:
            series_bond=series_bond,
            changeset=changeset,

            # copied fields:
            origin=series_bond.origin,
            origin_issue=series_bond.origin_issue,
            target=series_bond.target,
            target_issue=series_bond.target_issue,
            bond_type=series_bond.bond_type,
            notes=series_bond.notes)

        revision.save()
        return revision


def get_series_bond_field_list():
    return ['bond_type', 'notes']


class SeriesBondRevision(Revision):
    class Meta:
        db_table = 'oi_series_bond_revision'
        ordering = ['-created', '-id']
        get_latest_by = "created"

    objects = SeriesBondRevisionManager()

    series_bond = models.ForeignKey(SeriesBond, on_delete=models.CASCADE,
                                    null=True, related_name='revisions')

    origin = models.ForeignKey(Series, on_delete=models.CASCADE,
                               null=True, related_name='origin_bond_revisions')
    origin_issue = models.ForeignKey(
      Issue, on_delete=models.CASCADE, null=True,
      related_name='origin_series_bond_revisions')
    target = models.ForeignKey(Series, on_delete=models.CASCADE, null=True,
                               related_name='target_bond_revisions')
    target_issue = models.ForeignKey(
      Issue, on_delete=models.CASCADE, null=True,
      related_name='target_series_bond_revisions')

    bond_type = models.ForeignKey(SeriesBondType, on_delete=models.CASCADE,
                                  null=True, related_name='bond_revisions')
    notes = models.TextField(max_length=255, default='', blank=True)

    def _field_list(self):
        return (['origin', 'origin_issue', 'target', 'target_issue'] +
                get_series_bond_field_list())

    def _get_blank_values(self):
        return {
            'origin': None,
            'origin_issue': None,
            'target': None,
            'target_issue': None,
            'bond_type': None,
            'notes': '',
        }

    def _start_imp_sum(self):
        self._seen_origin = False
        self._seen_target = False

    def _imps_for(self, field_name):
        """
        Only one point per origin/target change
        """
        if field_name in ('origin', 'origin_issue'):
            if not self._seen_origin:
                self._seen_origin = True
                return 1
        if field_name in ('target',
                          'target_issue'):
            if not self._seen_target:
                self._seen_target = True
                return 1
        if field_name in get_series_bond_field_list():
            return 1
        return 0

    def _get_source(self):
        return self.series_bond

    def _get_source_name(self):
        return 'series_bond'

    def _queue_name(self):
        return '%s continues at %s' % (self.origin, self.target)

    def commit_to_display(self):
        series_bond = self.series_bond
        if self.deleted:
            for revision in series_bond.revisions.all():
                setattr(revision, "series_bond_id", None)
                revision.save()
            series_bond.delete()
            return

        if series_bond is None:
            series_bond = SeriesBond()
        series_bond.origin = self.origin
        series_bond.origin_issue = self.origin_issue
        series_bond.target = self.target
        series_bond.target_issue = self.target_issue
        series_bond.notes = self.notes
        series_bond.bond_type = self.bond_type

        series_bond.save()
        if self.series_bond is None:
            self.series_bond = series_bond
            self.save()

    def __str__(self):
        if self.origin_issue:
            object_string = '%s' % self.origin_issue
        else:
            object_string = '%s' % self.origin
        if self.target_issue:
            object_string += ' continues at %s' % self.target_issue
        else:
            object_string += ' continues at %s' % self.target
        return object_string


