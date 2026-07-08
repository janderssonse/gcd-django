# -*- coding: utf-8 -*-
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

from functools import reduce

# Base revision layer (roadmap C1). Re-exported here so the historical import
# surface (from apps.oi.models import Revision, Changeset, CTYPES, ...) is
# unchanged and so the concrete entity revisions below can reference it.
from apps.oi.models.base import (  # noqa: F401
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

# publisher cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.publisher import (  # noqa: F401
    PublisherRevisionBase, PublisherRevision, IndiciaPublisherRevision,
    BrandGroupRevision, BrandRevision, PreviewBrand,
    get_brand_use_field_list, BrandUseRevision, PrinterRevision,
    IndiciaPrinterRevision)

# cover cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.cover import (  # noqa: F401
    CoverRevisionManager, CoverRevision)

LANGUAGE_STATS = ['de']

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


def get_issue_field_list():
    return ['number', 'title', 'no_title', 'volume',
            'no_volume', 'volume_not_printed', 'display_volume_with_number',
            'indicia_publisher', 'indicia_pub_not_printed', 'brand_emblem',
            'no_brand', 'publication_date', 'year_on_sale',
            'month_on_sale', 'day_on_sale', 'on_sale_date_uncertain',
            'key_date', 'indicia_frequency', 'no_indicia_frequency', 'price',
            'page_count', 'page_count_uncertain', 'editing', 'no_editing',
            'indicia_printer', 'indicia_printer_not_printed',
            'indicia_printer_sourced_by',
            'isbn', 'no_isbn', 'barcode', 'no_barcode', 'rating', 'no_rating',
            'notes', 'keywords']


class PublisherCodeNumberRevision(Revision):
    class Meta:
        db_table = 'oi_issue_code_number_revision'

    publisher_code_number = models.ForeignKey(PublisherCodeNumber,
                                              on_delete=models.CASCADE,
                                              null=True,
                                              related_name='revisions')

    number = models.CharField(
      max_length=50, db_index=True,
      help_text='structured publisher code number, from cover or indicia')
    number_type = models.ForeignKey(CodeNumberType, on_delete=models.CASCADE)
    issue_revision = models.ForeignKey(
      'IssueRevision', on_delete=models.CASCADE,
      related_name='publisher_code_number_revisions')

    source_name = 'publisher_code_number'
    source_class = PublisherCodeNumber

    @property
    def source(self):
        return self.publisher_code_number

    @source.setter
    def source(self, value):
        self.publisher_code_number = value

    def _pre_save_object(self, changes):
        self.publisher_code_number.issue = self.issue_revision.issue

    def _do_complete_added_revision(self, issue_revision):
        self.issue_revision = issue_revision

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        self.issue_revision = kwargs['issue_revision']

    def __str__(self):
        return "%s: %s (%s)" % (self.issue_revision, self.number,
                                self.number_type)

    ######################################
    # TODO old methods, t.b.c

    _base_field_list = ['number', 'number_type']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'number': '',
            'number_type': None,
            'issue': None,
        }

    def _imps_for(self, field_name):
        return 1


class IssueCreditRevision(Revision):
    class Meta:
        db_table = 'oi_issue_credit_revision'
        ordering = ['credit_type__sort_code', 'id']

    issue_credit = models.ForeignKey(IssueCredit, on_delete=models.CASCADE,
                                     null=True, related_name='revisions')

    creator = models.ForeignKey(CreatorNameDetail, on_delete=models.CASCADE)
    credit_type = models.ForeignKey(CreditType, on_delete=models.CASCADE)
    issue_revision = models.ForeignKey('IssueRevision',
                                       on_delete=models.CASCADE,
                                       related_name='issue_credit_revisions')

    is_credited = models.BooleanField(default=False, db_index=True)

    uncertain = models.BooleanField(default=False, db_index=True)

    credited_as = models.CharField(max_length=255, blank=True)

    # record for a wider range of work types, or how it is credited
    credit_name = models.CharField(max_length=255)

    is_sourced = models.BooleanField(default=False, db_index=True, blank=True)
    sourced_by = models.CharField(max_length=255, blank=True)

    source_name = 'issue_credit'
    source_class = IssueCredit

    @property
    def source(self):
        return self.issue_credit

    @source.setter
    def source(self, value):
        self.issue_credit = value

    def _pre_save_object(self, changes):
        self.issue_credit.issue = self.issue_revision.issue

    def _do_complete_added_revision(self, issue_revision):
        self.issue_revision = issue_revision

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        self.issue_revision = kwargs['issue_revision']

    def __str__(self):
        return "%s: %s (%s)" % (self.issue_revision, self.creator,
                                self.credit_type)

    ######################################
    # TODO old methods, t.b.c

    _base_field_list = ['creator', 'credit_type', 'is_credited', 'uncertain',
                        'credited_as', 'credit_name',
                        'is_sourced', 'sourced_by']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'creator': None,
            'credit_type': None,
            'issue': None,
            'is_credited': False,
            'is_sourced': False,
            'uncertain': False,
            'credited_as': '',
            'sourced_by': '',
            'credit_name': '',
        }

    def _imps_for(self, field_name):
        # imps already come from IssueRevision, since is_changed is True there
        return 0


class IssueRevision(Revision):
    class Meta:
        db_table = 'oi_issue_revision'
        ordering = ['-created', '-id']

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE,
                              null=True, related_name='revisions')

    # If not null, insert or move the issue after the given issue
    # when saving back the the DB. If null, place at the beginning of
    # the series.
    after = models.ForeignKey(
      Issue, on_delete=models.CASCADE, null=True, blank=True,
      related_name='after_revisions')

    # This is used *only* for multiple issues within the same changeset.
    # It does NOT correspond directly to gcd_issue.sort_code, which must be
    # calculated at the time the revision is committed.
    revision_sort_code = models.IntegerField(null=True)

    # When adding an issue, this requests the reservation upon approval of
    # the new issue.  The request will be granted unless an ongoing reservation
    # is in place at the time of approval.
    reservation_requested = models.BooleanField(default=False)

    number = models.CharField(max_length=50)

    title = models.CharField(max_length=255, default='', blank=True)
    no_title = models.BooleanField(default=False)

    volume = models.CharField(max_length=50, blank=True, default='')
    no_volume = models.BooleanField(default=False)
    volume_not_printed = models.BooleanField(default=False)
    display_volume_with_number = models.BooleanField(default=False)
    variant_of = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True,
                                   related_name='variant_revisions')
    variant_name = models.CharField(max_length=255, blank=True, default='')
    variant_cover_status = models.IntegerField(choices=VCS_Codes.choices,
                                               default=3, db_index=True)

    publication_date = models.CharField(max_length=255, blank=True, default='')
    key_date = models.CharField(
        max_length=10, blank=True, default='',
        validators=[RegexValidator(
            r'^(17|18|19|20)\d{2}(\.|-)(0[0-9]|1[0-3])(\.|-)\d{2}$')])
    year_on_sale = models.IntegerField(db_index=True, null=True, blank=True)
    month_on_sale = models.IntegerField(db_index=True, null=True, blank=True)
    day_on_sale = models.IntegerField(db_index=True, null=True, blank=True)
    on_sale_date_uncertain = models.BooleanField(default=False)
    indicia_frequency = models.CharField(max_length=255, blank=True,
                                         default='')
    no_indicia_frequency = models.BooleanField(default=False)

    price = models.CharField(max_length=255, blank=True, default='')
    page_count = models.DecimalField(max_digits=10, decimal_places=3,
                                     null=True, blank=True, default=None)
    page_count_uncertain = models.BooleanField(default=False)

    editing = models.TextField(blank=True, default='')
    no_editing = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')
    keywords = models.TextField(blank=True, default='')

    series = models.ForeignKey(Series, on_delete=models.CASCADE,
                               related_name='issue_revisions')
    indicia_publisher = models.ForeignKey(
      IndiciaPublisher, on_delete=models.CASCADE, null=True, blank=True,
      default=None, related_name='issue_revisions')
    indicia_pub_not_printed = models.BooleanField(default=False)
    brand_emblem = models.ManyToManyField(Brand, blank=True,
                                          related_name='issue_revisions')
    # brand = models.ForeignKey(
    #   Brand, on_delete=models.CASCADE, null=True, default=None, blank=True,
    #   related_name='issue_revisions_deprecated')
    # TODO when removing brand_emblem, remove msdropdown from revision_form_utils.html
    # and remove apps/oi/templates/forms/widgets/select_brand.html
    no_brand = models.BooleanField(default=False)
    indicia_printer = models.ManyToManyField(IndiciaPrinter, blank=True,
                                             related_name='issue_revisions')
    indicia_printer_not_printed = models.BooleanField(default=False)
    indicia_printer_sourced_by = models.CharField(max_length=255, blank=True)

    isbn = models.CharField(max_length=32, blank=True, default='')
    no_isbn = models.BooleanField(default=False)

    barcode = models.CharField(max_length=38, blank=True, default='')
    no_barcode = models.BooleanField(default=False)

    rating = models.CharField(max_length=255, blank=True, default='')
    no_rating = models.BooleanField(default=False)

    date_inferred = models.BooleanField(default=False)

    external_link_revisions = GenericRelation(ExternalLinkRevision)

    source_name = 'issue'
    source_class = Issue

    @property
    def source(self):
        return self.issue

    @source.setter
    def source(self, value):
        self.issue = value

    @property
    def series_changed(self):
        """ True if the series changed and this is neither add nor delete. """
        return ((not self.deleted) and
                (self.previous_revision is not None) and
                self.previous_revision.series != self.series)

    @classmethod
    def fork_variant(cls, issue, changeset,
                     variant_name, variant_cover_revision=None,
                     reservation_requested=False):
        current_variants = issue.variant_set.all().order_by('-sort_code')
        if current_variants:
            add_after = current_variants[0]
        else:
            add_after = issue

        variant_revision = IssueRevision.clone(
            issue, changeset, fork=True, exclude={
                'publication_date',
                'key_date',
                'on_sale_date',
                'on_sale_date_uncertain',
                'price',
                'brand_emblem',
                'no_brand',
                'isbn',
                'no_isbn',
                'barcode',
                'no_barcode',
                'keywords',
            })
        variant_revision.add_after = add_after
        variant_revision.variant_of = issue
        variant_revision.variant_name = variant_name
        variant_revision.reservation_requested = reservation_requested
        variant_revision.save()

        if variant_cover_revision:
            cover_sequence_revision = StoryRevision(
                changeset=changeset,
                type=StoryType.objects.get(name='cover'),
                no_script=True,
                pencils='?',
                inks='?',
                colors='?',
                no_letters=True,
                no_editing=True,
                sequence_number=0,
                page_count=2 if variant_cover_revision.is_wraparound else 1)
            cover_sequence_revision.save()
        else:
            cover_sequence_revision = None

        return variant_revision, cover_sequence_revision

    @classmethod
    def _get_stats_category_field_tuples(cls):
        return frozenset({('series', 'country',), ('series', 'language',)})

    @classmethod
    def _get_conditional_field_tuple_mapping(cls):
        has_title = ('series', 'has_issue_title')
        has_barcode = ('series', 'has_barcode')
        has_isbn = ('series', 'has_isbn')
        has_volume = ('series', 'has_volume')
        has_ind_freq = ('series', 'has_indicia_frequency')
        has_ind_print = ('series', 'has_indicia_printer')
        return {
            'title': has_title,
            'no_title': has_title,
            'barcode': has_barcode,
            'no_barcode': has_barcode,
            'isbn': has_isbn,
            'no_isbn': has_isbn,
            'valid_isbn': has_isbn,
            'volume': has_volume,
            'no_volume': has_volume,
            'display_volume_with_issue': has_volume,
            'indicia_frequency': has_ind_freq,
            'no_indicia_frequency': has_ind_freq,
            'indicia_printer': has_ind_print,
            'indicia_printer_not_printed': has_ind_print,
        }

    @classmethod
    def _get_parent_field_tuples(cls):
        # There are several routes to a publisher object, but
        # if there are differences, it is the publisher of the series
        # that should get the count adjustments.
        return frozenset({
            ('series',),
            ('series', 'publisher'),
            ('indicia_publisher',),
            ('brand_emblem',),
            ('brand_emblem', 'group'),
            ('indicia_printer',),
        })

    def compare_changes(self, compare_revision=None):
        super(IssueRevision, self).compare_changes(
          compare_revision=compare_revision)
        if not self.deleted and not self.changed['editing']:
            if self.changeset.change_type == CTYPES['issue_bulk']:
                if not self.changeset.issuecreditrevisions.exists():
                    return
            credits = self.issue_credit_revisions.filter(
                           credit_type__id=6)
            if not compare_revision:
                compare_revision = self.previous()
            if not credits and compare_revision and \
               compare_revision.issue_credit_revisions.filter(
                  credit_type__id=6).exists():
                # compare against other issue, either we get it or we fetch it
                self.changed['editing'] = True
                self.is_changed = True
            elif credits:
                for credit in credits:
                    credit.compare_changes()
                    if credit.is_changed:
                        self.changed['editing'] = True
                        self.is_changed = True
                        break

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        source = fork_source if fork_source else self.issue
        if source.on_sale_date and 'on_sale_date' not in exclude:
            (self.year_on_sale,
             self.month_on_sale,
             self.day_on_sale) = on_sale_date_fields(source.on_sale_date)

    def _do_complete_added_revision(self, series, variant_of=None):
        """
        Do the necessary processing to complete the fields of a new
        issue revision for adding a record before it can be saved.
        """
        self.series = series
        if variant_of:
            self.variant_of = variant_of

    def _same_series_revisions(self):
        return self.changeset.issuerevisions.filter(series=self.series)

    def _same_series_open_with_after(self):
        return self._same_series_revisions().filter(after__isnull=False,
                                                    committed=None)

    def _open_prereq_revisions(self):
        # Adds and moves go first to last, deletes last to first.
        if self.deleted:
            return self._same_series_revisions()\
                       .exclude(id__lte=self.id) \
                       .filter(committed=None) \
                       .order_by('-revision_sort_code')
        else:
            return self._same_series_revisions().exclude(id__gte=self.id) \
                                                .filter(committed=None) \
                                                .filter(issue=None) \
                                                .order_by('revision_sort_code')

    def _committed_prereq_revisions(self):
        # We pop off of open prereqs and push onto committed, so reverse sort.
        sort = 'revision_sort_code' if self.deleted else '-revision_sort_code'
        return self._same_series_revisions().exclude(id=self.id) \
                                            .filter(committed=True) \
                                            .order_by(sort)

    def _pre_commit_check(self):
        # If any other issue from this series has been committed, we have
        # already gone through this logic, so skip it.
        if self._same_series_revisions().filter(committed=True).exists():
            return

        # Verify that we have at most one uncommitted revision with this
        # series that has a non-null 'after' field.  This means that for now
        # we can only support one contiguous run of added/moved issues per
        # series.
        #
        # TODO: This may need further tweaking for various cases of working
        #       with variants, moving covers, etc. but is sufficient for
        #       general single and bulk issue operations.
        after = self._same_series_open_with_after()
        if after.count() > 1:
            raise ValueError(
                ("%s, %s: Only one IssueRevision per series within a "
                 "changeset can have 'after' set.  All others are assumed "
                 "to follow it based on the 'revision_sort_code' field.") %
                (self.changeset, self))
        if after.exists() and (after.first() !=
                               self._same_series_revisions()
                                   .filter(issue=None)
                                   .order_by('revision_sort_code')
                                   .first()):
            raise ValueError(
                ("%s, %s: The IssueRevision that specifies an 'after' must "
                 "have the lowest revision_sort_code.") %
                (self.changeset, after.first()))

    def _ensure_sort_code_space(self):
        first_rev = self._same_series_open_with_after().first()
        after_code = -1 if first_rev is None else first_rev.after.sort_code

        # Include deleted issues due to unique constraint on sort_code.
        later_issues = Issue.objects.filter(
            series=self.series,
            sort_code__gt=after_code).order_by('-sort_code')

        if not later_issues.exists():
            # We're appending to the series, no space needed.
            return

        num_issues = self._same_series_revisions().count()
        if later_issues.last().sort_code - after_code > num_issues:
            # Someone else already made space here.
            return

        for later_issue in later_issues:
            later_issue.sort_code += num_issues
            later_issue.save()

    def _handle_prerequisites(self, changes):
        if self.edited and not self.series_changed:
            # order of revision commit doesn't matter, as we do issue
            # sort_code reorderings separately from the main editing
            # workflow, at least for now.
            return

        if not self.deleted:
            self._ensure_sort_code_space()

        current_prereq_qs = self._open_prereq_revisions().all()
        current_prereq_count = current_prereq_qs.count()

        stats_changed = False
        while current_prereq_count:
            stats_changed = True
            current_prereq_qs.first().commit_to_display()
            # Always eval a new queryset as committing may cause other commits.
            # Calling all() produces an identical but unevaluated queryset.
            current_prereq_qs = current_prereq_qs.all()
            new_prereq_count = current_prereq_qs.count()

            if new_prereq_count >= current_prereq_count:
                # We should never *gain* revisions- even if we create
                # revisions during a commit, those newly created revisions
                # should themselves be committed before the other commit
                # completes.  Prevent infinite loops by raising.
                # TODO we can add revisions for later commit in some
                #      cases, e.g. when they are in a later part of
                #      the itertools.chain. Check on this assumption.
                raise RuntimeError("Committing revisions did not reduce the "
                                   "number of uncommitted revisions!")

            current_prereq_count = new_prereq_count

        # refresh the series, otherwise the updated issue_counts from the other
        # issues (i.e. current_prereq_qs) in a bulk-add are overwritten
        # TODO rethink this handling, rethink F
        # TODO what if series changes publisher
        if stats_changed:
            self.series.refresh_from_db()

    def _post_assign_fields(self, changes):
        self.issue.on_sale_date = on_sale_date_as_string(self)

        if self.series.has_isbn:
            self.issue.valid_isbn = validated_isbn(self.issue.isbn)

        # TODO: Support adding base + variant by adding a variant_of_rev
        #       field to IssueRevision and setting variant_of to the
        #       committed issue of the variant_of_rev field automatically,
        #       committing the variant_of_rev if necessary.
        #       Idea may be good for other new dependent object situations.
        if self.added or self.series_changed:
            if not self.after:
                # If we're handling a run of issues, this is the
                # previous issue in the run, if any.
                committed = self._committed_prereq_revisions().first()
                if committed:
                    self.after = committed.issue

            if self.after:
                self.issue.sort_code = self.after.sort_code + 1
            else:
                self.issue.sort_code = 0

    def _post_save_object(self, changes):
        self.series.set_first_last_issues()
        if self.series_changed:
            old_series = self.previous_revision.series
            old_series.set_first_last_issues()

            # new series might have gallery after move
            if not self.series.has_gallery and \
               self.issue.active_covers().count():
                self.series.has_gallery = True
                self.series.save(update_fields=['has_gallery'])

            # old series might have lost gallery after move
            if old_series.scan_count == 0:
                old_series.has_gallery = False
                old_series.save(update_fields=['has_gallery'])
        if self.source.variant_of and self.added:
            self.source.is_indexed = self.source.variant_of.is_indexed
            self.source.save()

    def _do_create_dependent_revisions(self, delete=False):
        for credit in self.issue.active_credits:
            credit_lock = _get_revision_lock(credit,
                                             changeset=self.changeset)
            if credit_lock is None:
                raise IntegrityError("needed Credit lock not possible")
            credit_revision = IssueCreditRevision.clone(
                credit, self.changeset, issue_revision=self)
            if delete:
                credit_revision.deleted = self.deleted
                credit_revision.save()
        for story in self.issue.active_stories():
            # currently stories cannot be reserved without the issue, but
            # check anyway
            # TODO check if transaction rollback works
            story_lock = _get_revision_lock(story, changeset=self.changeset)
            if story_lock is None:
                raise IntegrityError("needed Story lock not possible")
            story_revision = StoryRevision.clone(story, self.changeset)
            if delete:
                story_revision.toggle_deleted()
            for credit in story.active_credits:
                credit_lock = _get_revision_lock(credit,
                                                 changeset=self.changeset)
                if credit_lock is None:
                    raise IntegrityError("needed Credit lock not possible")
                credit_revision = StoryCreditRevision.clone(
                  credit, self.changeset, story_revision=story_revision)
                if delete:
                    credit_revision.deleted = story_revision.deleted
                    credit_revision.save()
            for character_order in story.character_orders.all():
                order_lock = _get_revision_lock(character_order,
                                                changeset=self.changeset)
                if order_lock is None:
                    raise IntegrityError("needed Order lock not possible")
                order_revision = CharacterOrderRevision.clone(
                  character_order, self.changeset,
                  story_revision=story_revision)
                if delete:
                    order_revision.deleted = story_revision.deleted
                    order_revision.save()
            for character in story.active_characters:
                character_lock = _get_revision_lock(character,
                                                    changeset=self.changeset)
                if character_lock is None:
                    raise IntegrityError("needed Character lock not possible")
                character_revision = StoryCharacterRevision.clone(
                  character, self.changeset, story_revision=story_revision)
                if delete:
                    character_revision.deleted = story_revision.deleted
                    character_revision.save()
                for order in character.characterorder_set.all():
                    order_code = character\
                      .characterthroughorder_set.get(order=order).order_code
                    order_revision = order.revisions.get(
                      changeset=self.changeset)
                    order_revision.character_revisions.add(
                      character_revision,
                      through_defaults={'order_code': order_code})
            for group in story.active_groups:
                group_lock = _get_revision_lock(group,
                                                changeset=self.changeset)
                if group_lock is None:
                    raise IntegrityError("needed Group lock not possible")
                group_revision = StoryGroupRevision.clone(
                  group, self.changeset, story_revision=story_revision)
                if delete:
                    group_revision.deleted = story_revision.deleted
                    group_revision.save()
        for code_number in self.issue.active_code_numbers():
            code_number_lock = _get_revision_lock(code_number,
                                                  changeset=self.changeset)
            if code_number_lock is None:
                raise IntegrityError("needed Code Number lock not possible")
            code_number_revision = PublisherCodeNumberRevision.clone(
                code_number, self.changeset, issue_revision=self)
            if delete:
                code_number_revision.deleted = self.deleted
                code_number_revision.save()

        if delete:
            for cover in self.issue.active_covers():
                # cover can be reserved, so this can fail
                # TODO check if transaction rollback works
                cover_lock = _get_revision_lock(cover,
                                                changeset=self.changeset)
                if cover_lock is None:
                    raise IntegrityError("needed Cover lock not possible")
                # TODO change CoverRevision handling to normal one
                cover_revision = CoverRevision(changeset=self.changeset,
                                               issue=cover.issue,
                                               cover=cover, deleted=True)
                cover_revision.save()

    def _handle_dependents(self, changes):
        # These story revisions will handle their own stats when committed.
        # They will also update the issue's is_indexed field.
        for story in self.changeset.storyrevisions.filter(issue=None):
            story.issue = self.issue
            story.save()

        # -------------------------------------------------------------------
        # Cross-Series Variant Stat Routing
        # -------------------------------------------------------------------
        # When a base issue moves to a new series, its variants do not
        # automatically follow it. This means a variant left behind in the
        # old series just became a "cross-series" variant (which contributes
        # +1 to its series issue_count), or vice-versa. Adjust the cached
        # counts of the affected series.
        if changes.get('series changed'):
            old_series = changes.get('old series')
            new_series = self.issue.series

            IssueClass = type(self.issue)
            variants = IssueClass.objects.filter(variant_of=self.issue,
                                                 deleted=False)

            for variant in variants:
                # 1. Variant left behind:
                # Goes from Standard -> Cross-Series (+1)
                if variant.series == old_series and \
                        variant.series != new_series:
                    variant.series.issue_count += 1
                    variant.series.save(update_fields=['issue_count'])

                # 2. Base issue returns:
                # Goes from Cross-Series -> Standard (-1)
                elif variant.series != old_series and \
                        variant.series == new_series:
                    if variant.series.issue_count > 0:
                        variant.series.issue_count -= 1
                        variant.series.save(update_fields=['issue_count'])


    def extra_forms(self, request):
        from apps.oi.forms import IssueRevisionFormSet, \
            PublisherCodeNumberFormSet
        credits_formset = IssueRevisionFormSet(
          request.POST or None,
          instance=self,
          queryset=self.issue_credit_revisions.filter(deleted=False))
        if self.series.has_publisher_code_number:
            code_number_formset = PublisherCodeNumberFormSet(
              request.POST or None,
              instance=self,
              queryset=self.publisher_code_number_revisions.filter(
                       deleted=False)
              )
        else:
            code_number_formset = None
        external_link_formset = self._create_external_link_formset(request)
        return {'credits_formset': credits_formset,
                'code_number_formset': code_number_formset,
                'external_link_formset': external_link_formset}

    def process_extra_forms(self, extra_forms):
        credits_formset = extra_forms['credits_formset']
        _process_formset(self, credits_formset, revision_type='issue_revision')
        removed_credits = credits_formset.deleted_forms
        if removed_credits:
            _removed_related_objects(removed_credits, 'issue_credit')

        self._process_external_link_formset(extra_forms)

        if self.series.has_publisher_code_number:
            code_number_formset = extra_forms['code_number_formset']
            _process_formset(self, code_number_formset,
                             revision_type='issue_revision')
            removed_code_numbers = code_number_formset.deleted_forms
            if removed_code_numbers:
                _removed_related_objects(removed_code_numbers,
                                         'publisher_code_number')

    def migrate_credits(self):
        if self.editing and self.editing != '?':
            credits = self.editing.strip(';')
            credits = credits.split(';')
            old_credits = ''
            for credit in credits:
                credit = credit.strip()
                save_credit = credit
                credit = credit.replace('  ', ' ')
                if credit.strip()[-1] == '?':
                    credit = credit[:-1]
                    uncertain = True
                else:
                    uncertain = False
                is_credited = False
                credited_as = ''
                if credit.find('(') > 1:
                    note = credit[credit.find('(')+1:].strip()
                    end_note = note.find(')')
                    remainder_note = note[end_note+1:].strip()
                    note = note[:end_note].strip()
                    save_credit = credit
                    credit = credit[:credit.find('(')-1]
                    if note in ['credited', 'kreditert']:
                        is_credited = True
                        note = ''
                        if remainder_note:
                            if remainder_note.find('as ') > 1:
                                credited_as = remainder_note[
                                                remainder_note.find('as ')+3:
                                                remainder_note.find(']')]
                            else:
                                note = remainder_note
                    else:
                        note = save_credit[save_credit.find('('):].strip()
                else:
                    note = ''
                if credit.find('[') > 1:
                    value = credit[credit.find('[')+1:]
                    value = value[value.find(' ')+1:]
                    value = value.strip().strip(']')
                    credit = value

                creator = CreatorNameDetail.objects.filter(name=credit,
                                                           deleted=False)
                # exclude ghost names
                creator = creator.exclude(type=12)

                if creator.count() == 1:
                    creator = creator.get()
                    if uncertain and not creator.is_official_name:
                        if creator.in_script == creator.creator\
                           .active_names().get(is_official_name=True)\
                           .in_script:
                            creator = creator.creator.active_names().get(
                                                is_official_name=True)
                    if note and note[0] == '(' and note[-1] == ')':
                        note = note[1:-1]
                    if note == '':
                        note = 'editor'
                    credit_revision = IssueCreditRevision(
                        changeset=self.changeset,
                        issue_revision_id=self.id,
                        creator=creator,
                        credit_type_id=CREDIT_TYPES['editing'],
                        is_credited=is_credited,
                        credited_as=credited_as,
                        uncertain=uncertain,
                        credit_name=note)
                    credit_revision.save()
                else:
                    if old_credits:
                        old_credits += '; ' + save_credit
                    else:
                        old_credits = save_credit
            setattr(self, 'editing', old_credits)
            self.save()

    def old_credits(self):
        credit = self.editing
        if credit:
            for s in credit.split(";"):
                stripped = s.strip()
                if not stripped.startswith('?'):
                    return True
        return False

    def get_absolute_url(self):
        if self.issue is None:
            return "/issue/revision/%i/preview" % self.id
        return self.issue.get_absolute_url()

    ######################################
    # TODO old methods, t.b.c

    @property
    def display_number(self):
        number = issue_descriptor(self)
        if number:
            return '#' + number
        else:
            return ''

    @property
    def other_issue_revision(self):
        if self.changeset.change_type in [CTYPES['variant_add'],
                                          CTYPES['two_issues']]:
            if not hasattr(self, '_saved_other_issue'):
                self._saved_other_issue_revision = self.changeset\
                    .issuerevisions.exclude(issue=self.issue)[0]
            return self._saved_other_issue_revision
        elif self.changeset.change_type == CTYPES['issue_add']:
            return None
        else:
            raise ValueError

    def can_add_reprints(self):
        if self.variant_of and self.ordered_story_revisions().count() > 0:
            return False
        return True

    # we need two checks if relevant reprint revisions exist:
    # 1) revisions which are active and link self.issue with a story/issue
    #    in the current direction under consideration
    # 2) existing reprints which are locked and which link self.issue
    #    with a story/issue in the current direction under consideration
    # if this is the case we return reprintrevisions and not reprint links
    # returned reprint links are three cases:
    # a) revisions in the current changeset which link self.issue with a
    #    story/issue in the current direction under consideration
    # b) newly added and active revisions in other changesets
    #    we do not need .exclude(changeset__id=self.changeset_id)\ the new
    #    ones from the current changeset we want anyway
    # c) for the current corresponding reprint links the latest revisions
    #    which are not in the current changeset, the latest can be fetched
    #    via next_revision=None, that way we get either approved or active ones

    def old_revisions_base(self):
        revs = ReprintRevision.objects \
                              .exclude(changeset__id=self.changeset_id)\
                              .exclude(changeset__state=states.DISCARDED)
        return revs

    def from_reprints_oi(self, preview=False):
        if self.issue is None:
            return Reprint.objects.none()
        from_reprints = self.issue.from_reprints.all()
        from_reprints_ids = from_reprints.values_list('id', flat=True)
        if self.issue.target_reprint_revisions.active_set().count() \
                or RevisionLock.objects.filter(
                  object_id__in=from_reprints_ids).exists():
            # reprint revisions of the story that are currently in
            # active changesets
            new_revisions = self.issue.target_reprint_revisions.active_set()\
                                .filter(target=None, target_revision=None)
            if preview:
                # new reprint revisions of story that are in other active
                # changesets are not shown in preview, neither are deleted ones
                new_revisions = new_revisions.exclude(deleted=True)\
                                .filter(changeset__id=self.changeset_id)
            new_revisions_ids = new_revisions.values_list('id', flat=True)
            if not preview:
                # reprint revisions of story that represent current state,
                # but which are not edited in this changeset,
                old_revisions = self.issue.target_reprint_revisions\
                                    .filter(next_revision=None)\
                                    .filter(target=None, target_revision=None)\
                                    .exclude(changeset__id=self.changeset_id)\
                                    .exclude(deleted=True)\
                                    .exclude(changeset__state=states.DISCARDED)
                # reprint revisions of story that are edited in
                # other active changesets
                next_revisions_ids = self.issue.target_reprint_revisions\
                    .exclude(next_revision=None)\
                    .filter(target=None, target_revision=None)\
                    .exclude(next_revision__changeset__id=self.changeset_id)\
                    .filter(next_revision__changeset__state__in=states.ACTIVE)\
                    .values_list('next_revision__id', flat=True)
            else:
                # revisions of story that are not currently not being edited
                old_revisions = self.issue.target_reprint_revisions\
                                    .filter(next_revision=None,
                                            target=None, target_revision=None,
                                            changeset__state=states.APPROVED)\
                                    .exclude(deleted=True)
                next_revisions_ids = []
            old_revisions_ids = old_revisions.values_list('id', flat=True)
            revisions_ids = set(new_revisions_ids) | set(old_revisions_ids) | \
                set(next_revisions_ids)
            return ReprintRevision.objects.filter(id__in=revisions_ids)
        else:
            return from_reprints

    def from_story_reprints_oi(self, preview=False):
        return self.from_reprints_oi(preview=preview).exclude(origin=None)

    def from_issue_reprints_oi(self, preview=False):
        return self.from_reprints_oi(preview=preview).filter(origin=None)

    def to_reprints_oi(self, preview=False):
        if self.issue is None:
            return Reprint.objects.none()
        to_reprints = self.issue.to_reprints.all()
        to_reprints_ids = to_reprints.values_list('id', flat=True)
        if self.issue.origin_reprint_revisions.active_set().count() \
                or RevisionLock.objects.filter(
                  object_id__in=to_reprints_ids).exists():
            # reprint revisions of the story that are currently in
            # active changesets
            new_revisions = self.issue.origin_reprint_revisions.active_set()\
                                .filter(origin=None, origin_revision=None)
            if preview:
                # new reprint revisions of story that are in other active
                # changesets are not shown in preview, neither are deleted ones
                new_revisions = new_revisions.exclude(deleted=True)\
                                .filter(changeset__id=self.changeset_id)
            new_revisions_ids = new_revisions.values_list('id', flat=True)
            if not preview:
                # reprint revisions of story that represent current state,
                # but which are not edited in this changeset,
                old_revisions = self.issue.origin_reprint_revisions\
                        .filter(next_revision=None)\
                        .filter(origin=None, origin_revision=None)\
                        .exclude(changeset__id=self.changeset_id)\
                        .exclude(changeset__state=states.DISCARDED)\
                        .exclude(deleted=True)
                # reprint revisions of story that are edited in
                # other active changesets
                next_revisions_ids = self.issue.origin_reprint_revisions\
                    .exclude(next_revision=None)\
                    .filter(origin=None, origin_revision=None)\
                    .exclude(next_revision__changeset__id=self.changeset_id)\
                    .filter(next_revision__changeset__state__in=states.ACTIVE)\
                    .values_list('next_revision__id', flat=True)
            else:
                # revisions of story that are not currently not being edited
                old_revisions = self.issue.origin_reprint_revisions\
                                    .filter(next_revision=None,
                                            origin=None, origin_revision=None,
                                            changeset__state=states.APPROVED)\
                                    .exclude(deleted=True)
                next_revisions_ids = []
            old_revisions_ids = old_revisions.values_list('id', flat=True)
            revisions_ids = set(new_revisions_ids) | set(old_revisions_ids) | \
                set(next_revisions_ids)
            return ReprintRevision.objects.filter(id__in=revisions_ids)
        else:
            return to_reprints

    def to_story_reprints_oi(self, preview=False):
        return self.to_reprints_oi(preview=preview).exclude(target=None)

    def to_issue_reprints_oi(self, preview=False):
        return self.to_reprints_oi(preview=preview).filter(target=None)

    def has_reprint_revisions(self):
        if self.issue is None:
            return False
        if self.issue.target_reprint_revisions\
               .filter(changeset__id=self.changeset_id)\
               .filter(target=None, target_revision=None).exists():
            return True
        elif self.issue.origin_reprint_revisions\
                 .filter(changeset__id=self.changeset_id)\
                 .filter(origin=None, origin_revision=None).exists():
            return True
        if self.issue.to_reprints\
               .filter(revisions__changeset=self.changeset)\
               .exists():
            return True
        if self.issue.from_reprints\
               .filter(revisions__changeset=self.changeset)\
               .exists():
            return True
        if self.changeset.state == states.APPROVED:
            active = ReprintRevision.objects.\
                filter(next_revision__in=self.changeset.reprintrevisions.all())
            if active.filter(origin_issue=self.issue).exists():
                return True
            if active.filter(target_issue=self.issue).exists():
                return True
        return False

    # IssueRevisions cannot have reprint links, need to fake for compare-view,
    def _empty_reprint_revisions(self):
        return ReprintRevision.objects.none()
    origin_reprint_revisions = property(_empty_reprint_revisions)
    target_reprint_revisions = property(_empty_reprint_revisions)

    # TODO what can be re-used/share with PreviewIssue
    def active_stories(self):
        return self.story_set.exclude(deleted=True)

    @property
    def story_set(self):
        return self.ordered_story_revisions()

    def _story_revisions(self):
        # previous_revision is read by previous()/compare_changes, and the
        # feature m2m is iterated per story when rendering compare/preview,
        # so pull them in up front to avoid a query per story revision.
        if self.source is None:
            return self.changeset.storyrevisions.filter(issue__isnull=True)\
                                 .select_related('changeset', 'type',
                                                 'previous_revision')\
                                 .prefetch_related('feature_object',
                                                   'feature_logo')
        return self.changeset.storyrevisions.filter(issue=self.source)\
                             .select_related('changeset', 'issue', 'type',
                                             'previous_revision')\
                             .prefetch_related('feature_object',
                                               'feature_logo')

    def ordered_story_revisions(self):
        return self._story_revisions().order_by('sequence_number')

    def code_number_revisions(self):
        return self.changeset.publishercodenumberrevisions.filter(
          issue_revision=self)

    def next_sequence_number(self):
        stories = self._story_revisions()
        if stories.count():
            return stories.order_by('-sequence_number')[0].sequence_number + 1
        return 0

    def _field_list(self):
        fields = get_issue_field_list()
        if self.changeset.change_type == CTYPES['issue_add'] or \
           self.changeset.change_type == CTYPES['variant_add'] and \
           self.variant_of:
            fields = ['after'] + fields
        if not self.series.has_barcode and \
           self.changeset.change_type != CTYPES['issue_bulk']:
            fields.remove('barcode')
            fields.remove('no_barcode')
        if not self.series.has_indicia_frequency and \
           self.changeset.change_type != CTYPES['issue_bulk']:
            fields.remove('indicia_frequency')
            fields.remove('no_indicia_frequency')
        if not self.series.has_indicia_printer and \
           self.changeset.change_type != CTYPES['issue_bulk']:
            fields.remove('indicia_printer')
            fields.remove('indicia_printer_not_printed')
        if not self.series.has_isbn and \
           self.changeset.change_type != CTYPES['issue_bulk']:
            fields.remove('isbn')
            fields.remove('no_isbn')
        if not self.series.has_issue_title and \
           self.changeset.change_type != CTYPES['issue_bulk']:
            fields.remove('title')
            fields.remove('no_title')
        if not self.series.has_volume and \
           self.changeset.change_type != CTYPES['issue_bulk']:
            fields.remove('volume')
            fields.remove('no_volume')
            fields.remove('volume_not_printed')
            fields.remove('display_volume_with_number')
        if self.variant_of or (self.issue and self.issue.variant_set.count()) \
           or self.changeset.change_type == CTYPES['variant_add']:
            fields = fields[0:1] + ['variant_name'] + fields[1:]
            if self.variant_of:
                fields = fields[0:2] + ['variant_cover_status'] + fields[2:]

        if self.previous() and (self.previous().series != self.series):
            fields = ['series'] + fields
        return fields

    def _get_blank_values(self):
        return {
            'number': '',
            'title': '',
            'no_title': False,
            'volume': '',
            'no_volume': False,
            'volume_not_printed': False,
            'display_volume_with_number': None,
            'publication_date': '',
            'price': '',
            'key_date': '',
            'year_on_sale': None,
            'month_on_sale': None,
            'day_on_sale': None,
            'on_sale_date_uncertain': False,
            'indicia_frequency': '',
            'no_indicia_frequency': False,
            'indicia_printer': None,
            'indicia_printer_not_printed': False,
            'indicia_printer_sourced_by': '',
            'series': None,
            'indicia_publisher': None,
            'indicia_pub_not_printed': False,
            'brand_emblem': None,
            'no_brand': False,
            'page_count': None,
            'page_count_uncertain': False,
            'editing': '',
            'no_editing': False,
            'isbn': '',
            'no_isbn': False,
            'barcode': '',
            'no_barcode': False,
            'rating': '',
            'no_rating': False,
            'notes': '',
            'sort_code': None,
            'after': None,
            'variant_name': '',
            'variant_cover_status': 3,
            'keywords': ''
        }

    def _start_imp_sum(self):
        self._seen_volume = False
        self._seen_title = False
        self._seen_indicia_publisher = False
        self._seen_indicia_frequency = False
        self._seen_indicia_printer = False
        self._seen_brand_emblem = False
        self._seen_page_count = False
        self._seen_editing = False
        self._seen_isbn = False
        self._seen_barcode = False
        self._seen_rating = False
        self._seen_on_sale_date = False

    def _imps_for(self, field_name):
        if field_name in ('number', 'publication_date', 'key_date', 'series',
                          'price', 'notes', 'variant_name',
                          'variant_cover_status', 'keywords'):
            return 1
        if not self._seen_volume and \
           field_name in ('volume', 'no_volume', 'volume_not_printed',
                          'display_volume_with_number'):
            self._seen_volume = True
            return 1
        if not self._seen_title and field_name in ('title', 'no_title'):
            self._seen_title = True
            return 1
        if not self._seen_indicia_publisher and \
           field_name in ('indicia_publisher', 'indicia_pub_not_printed'):
            self._seen_indicia_publisher = True
            return 1
        if not self._seen_indicia_frequency and \
           field_name in ('indicia_frequency', 'no_indicia_frequency'):
            self._seen_indicia_frequency = True
            return 1
        if not self._seen_indicia_printer and \
           field_name in ('indicia_printer', 'indicia_printer_not_printed'):
            self._seen_indicia_printer = True
            return 1
        if not self._seen_brand_emblem and field_name in ('brand_emblem',
                                                          'no_brand'):
            self._seen_brand_emblem = True
            return 1
        if not self._seen_page_count and \
           field_name in ('page_count', 'page_count_uncertain'):
            self._seen_page_count = True
            if field_name == 'page_count':
                return 1

            # checking the 'uncertain' box  without also at least guessing
            # the page count itself doesn't count as IMP-worthy information.
            if field_name == 'page_count_uncertain' and \
               self.page_count is not None:
                return 1
        if not self._seen_editing and field_name in ('editing', 'no_editing'):
            self._seen_editing = True
            return 1
        if not self._seen_isbn and field_name in ('isbn', 'no_isbn'):
            self._seen_isbn = True
            return 1
        if not self._seen_barcode and field_name in ('barcode', 'no_barcode'):
            self._seen_barcode = True
            return 1
        if not self._seen_rating and field_name in ('rating', 'no_rating'):
            self._seen_rating = True
            return 1
        if not self._seen_on_sale_date and \
           field_name in ('year_on_sale', 'month_on_sale',
                          'day_on_sale', 'on_sale_date_uncertain'):
            self._seen_on_sale_date = True
            if field_name in ('year_on_sale', 'month_on_sale', 'day_on_sale'):
                return 1

            if field_name == 'on_sale_date_uncertain':
                if self.year_on_sale or self.month_on_sale or self.day_on_sale:
                    return 1
        # Note, the "after" field does not directly contribute IMPs.
        return 0

    def _check_first_last(self):
        set_series_first_last(self.series)

    def full_name(self):
        if self.variant_name:
            return '%s %s [%s]' % (self.series.full_name(),
                                   self.display_number,
                                   self.variant_name)
        else:
            return '%s %s' % (self.series.full_name(), self.display_number)

    def short_name(self):
        if self.variant_name:
            return '%s %s [%s]' % (self.series.name,
                                   self.display_number,
                                   self.variant_name)
        else:
            return '%s %s' % (self.series.name, self.display_number)

    def __str__(self):
        """
        Re-implement locally instead of using self.issue because it may change.
        """
        if self.variant_name:
            return '%s %s [%s]' % (self.series, self.display_number,
                                   self.variant_name)
        elif self.display_number:
            return '%s %s' % (self.series, self.display_number)
        else:
            return '%s' % self.series


class PreviewIssue(Issue):
    # TODO add and use PreviewIssue.init
    class Meta:
        proxy = True

    def get_prev_next_issue(self):
        if self.id:
            return self._get_prev_next_issue()
        if self.after is not None:
            [p, n] = self.after.get_prev_next_issue()
            return [self.after, n]
        return [None, None]

    def active_variants(self):
        if self.id == 0:
            return Cover.objects.none()
        # TODO in case of variant add together with issue, would
        # need to do something like the following to be correct.
        # We can do something like this with other_variants, there
        # we have a list. Better to use that one in templates for checks
        # when displaying something which is preview-relevant.
        # maybe iterchain helps, but that does not provide a count
        # if self.revision.changeset.issuerevisions.filter(variant_of=self)\
        # .exists():
        # return (self._active_variants() | self.revision.changeset
        # .issuerevisions
        # .filter(variant_of=self))
        # else:
        return self._active_variants()

    def other_variants(self):
        if self.variant_of:
            variants = self.variant_of.active_variants()
            if self.id:
                variants = variants.exclude(id=self.id)
        else:
            variants = self.active_variants()
        variants = list(variants)

        # check for newly added variants
        if self.revision.changeset.issuerevisions.filter(variant_of=self,
                                                         issue=None)\
                                                 .exists():
            variants.extend(self.revision.changeset.issuerevisions
                                         .filter(variant_of=self,
                                                 issue=None))
        return variants

    def active_covers(self):
        if self.can_have_cover():
            if self.id != 0:
                return self._active_covers()
        return Cover.objects.none()

    @property
    def brand_emblem(self):
        return self.revision.brand_emblem.all()

    @property
    def credits(self):
        return self.revision.issue_credit_revisions.exclude(deleted=True)

    @property
    def active_credits(self):
        return self.revision.issue_credit_revisions.exclude(deleted=True)

    def active_printers(self):
        return self.revision.indicia_printer.all()

    def active_stories(self):
        stories = self.revision.story_set.exclude(deleted=True)\
                                     .order_by('sequence_number')\
                                     .select_related('type')
        active_stories = []
        for story in stories:
            preview_story = PreviewStory.init(story)
            preview_story.issue = self
            active_stories.append(preview_story)
        return active_stories

    def active_code_numbers(self):
        return self.revision.code_number_revisions()

    def shown_stories(self):
        if self.variant_of:
            if self.issuerevisions.filter(issue=self.variant_of).exists():
                # if base_issue is part of the changeset use the storyrevisions
                # TODO add and use PreviewIssue.init
                base_issue_revision = self.issuerevisions\
                                 .filter(issue=self.variant_of).get()
                base_issue = PreviewIssue(base_issue_revision.source)
                base_issue.storyrevisions = base_issue_revision.changeset\
                                                               .storyrevisions
                base_issue.id = base_issue_revision.source.id
                base_issue.revision = base_issue_revision
                base_issue.series = base_issue_revision.series
                stories = base_issue.active_stories()
            else:
                base_issue = self.variant_of
                stories = list(base_issue.active_stories())
        else:
            stories = self.active_stories()

        cover_story = None
        if self.series.is_comics_publication or \
           self.series.has_about_comics is True:
            if (len(stories) > 0) and stories[0].type_id == 6:
                cover_story = stories.pop(0)
                if self.variant_of:
                    # can have only one sequence, the variant cover
                    own_stories = self.active_stories()
                    if own_stories:
                        cover_story = own_stories[0]
            elif self.variant_of and len(self.active_stories()):
                cover_story = self.active_stories()[0]

        return cover_story, stories

    # we do not use ignore on preview, since target does not exist
    # for revision and property cannot be filtered on
    def has_reprints(self):
        """Simplifies UI checks for conditionals, notes and reprint fields"""
        return self.from_reprints.count() or \
            self.to_reprints.count() or \
            self.from_issue_reprints.count() or \
            self.to_issue_reprints.count()

    @property
    def from_reprints(self):
        return self.revision.from_reprints_oi(preview=True)

    @property
    def from_story_reprints(self):
        return self.revision.from_story_reprints_oi(preview=True)

    @property
    def from_issue_reprints(self):
        return self.revision.from_issue_reprints_oi(preview=True)

    @property
    def to_reprints(self):
        return self.revision.to_reprints_oi(preview=True)

    @property
    def to_story_reprints(self):
        return self.revision.to_story_reprints_oi(preview=True)

    @property
    def to_issue_reprints(self):
        return self.revision.to_issue_reprints_oi(preview=True)

    def has_keywords(self):
        return self.revision.has_keywords()


def get_story_field_list():
    return ['sequence_number', 'title', 'title_inferred', 'first_line',
            'type', 'feature', 'feature_object', 'feature_logo', 'story_arc',
            'genre', 'job_number', 'page_count', 'page_count_uncertain',
            'script', 'no_script', 'pencils', 'no_pencils', 'inks', 'no_inks',
            'colors', 'no_colors', 'letters', 'no_letters',
            'editing', 'no_editing', 'characters', 'universe',
            'synopsis', 'reprint_notes', 'notes', 'keywords']


class StoryCreditRevision(Revision):
    class Meta:
        db_table = 'oi_story_credit_revision'
        ordering = ['credit_type__sort_code', 'id']

    story_credit = models.ForeignKey(StoryCredit, on_delete=models.CASCADE,
                                     null=True, related_name='revisions')

    creator = models.ForeignKey(CreatorNameDetail, on_delete=models.CASCADE)
    credit_type = models.ForeignKey(CreditType, on_delete=models.CASCADE)
    story_revision = models.ForeignKey('StoryRevision',
                                       on_delete=models.CASCADE,
                                       related_name='story_credit_revisions')

    is_credited = models.BooleanField(default=False, db_index=True)
    is_signed = models.BooleanField(default=False, db_index=True)
    signature = models.ForeignKey(CreatorSignature, on_delete=models.CASCADE,
                                  blank=True, null=True)

    uncertain = models.BooleanField(default=False, db_index=True)

    signed_as = models.CharField(max_length=255, blank=True)
    credited_as = models.CharField(max_length=255, blank=True)

    is_sourced = models.BooleanField(default=False, db_index=True, blank=True)
    sourced_by = models.CharField(max_length=255, blank=True)

    # record for a wider range of creative work types, or how it is credited
    credit_name = models.CharField(max_length=255, blank=True)

    source_name = 'story_credit'
    source_class = StoryCredit

    @property
    def source(self):
        return self.story_credit

    @source.setter
    def source(self, value):
        self.story_credit = value

    def _handle_prerequisites(self, changes):
        if self.signed_as:
            creator = self.creator.creator
            signature = CreatorSignature.objects.filter(name=self.signed_as,
                                                        creator=creator,
                                                        generic=True,
                                                        deleted=False)
            if signature.count() > 1:
                for sig in signature:
                    if sig.name == self.signed_as:
                        signature = signature.filter(id=sig.id)
                        break
            if signature.count() == 1:
                self.signed_as = ''
                self.signature = signature.get()
            else:
                signature = CreatorSignatureRevision.objects.create(
                                                     name=self.signed_as,
                                                     creator=creator,
                                                     generic=True,
                                                     changeset=self.changeset)
                signature.commit_to_display()
                self.signed_as = ''
                self.signature = signature.creator_signature

        if self.credited_as:
            creator = self.creator.creator
            creator_name = creator.creator_names.filter(name=self.credited_as,
                                                        deleted=False)\
                                                .exclude(type__id__in=[3, 4])
            if creator_name.count() == 1:
                # database does not care about accents, etc., but python does
                if self.credited_as == creator_name.get().name:
                    self.credited_as = ''
                    self.creator = creator_name.get()

    def _pre_save_object(self, changes):
        self.story_credit.story = self.story_revision.story

    def _do_complete_added_revision(self, story_revision):
        self.story_revision = story_revision

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        self.story_revision = kwargs['story_revision']

    def __str__(self):
        return "%s: %s (%s)" % (self.story_revision, self.creator,
                                self.credit_type)

    ######################################
    # TODO old methods, t.b.c

    _base_field_list = ['creator', 'credit_type', 'is_credited', 'is_signed',
                        'uncertain', 'signature', 'signed_as', 'credited_as',
                        'credit_name', 'is_sourced', 'sourced_by']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'creator': None,
            'credit_type': None,
            'story': None,
            'is_credited': False,
            'is_signed': False,
            'is_sourced': False,
            'uncertain': False,
            'signature': None,
            'signed_as': '',
            'credited_as': '',
            'sourced_by': '',
            'credit_name': '',
        }

    def _imps_for(self, field_name):
        # imps already come from StoryRevision, since is_changed is True there
        return 0


class StoryCharacterRevision(Revision):
    class Meta:
        db_table = 'oi_story_character_revision'
        ordering = ['character__sort_name']

    story_character = models.ForeignKey(StoryCharacter, null=True,
                                        on_delete=models.CASCADE,
                                        related_name='revisions')

    character = models.ForeignKey(CharacterNameDetail,
                                  on_delete=models.CASCADE,
                                  related_name='story_character_revisions')
    universe = models.ForeignKey(Universe, null=True, blank=True,
                                 on_delete=models.CASCADE)
    story_revision = models.ForeignKey(
      'StoryRevision', on_delete=models.CASCADE,
      related_name='story_character_revisions')
    group = models.ManyToManyField(Group, blank=True)
    group_name = models.ManyToManyField(GroupNameDetail, blank=True)
    group_universe = models.ForeignKey(
      Universe, null=True, on_delete=models.CASCADE,
      related_name='story_character_in_group_revision')
    role = models.ForeignKey(CharacterRole, null=True, blank=True,
                             on_delete=models.CASCADE)
    is_flashback = models.BooleanField(default=False)
    is_origin = models.BooleanField(default=False)
    is_death = models.BooleanField(default=False)

    notes = models.TextField(blank=True)

    source_name = 'story_character'
    source_class = StoryCharacter

    @property
    def source(self):
        return self.story_character

    @source.setter
    def source(self, value):
        self.story_character = value

    def _pre_save_object(self, changes):
        self.story_character.story = self.story_revision.story

    def _do_complete_added_revision(self, story_revision):
        self.story_revision = story_revision

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        self.story_revision = kwargs['story_revision']

    @classmethod
    def copied_translation(cls, character, story_revision):
        """
        Given an existing character appearance, create a new revision based
        on it for a new character appearance with the copied character and data
        but a different translation.
        """
        language = story_revision.issue.series.language
        translations = character.character.character.translations(
            language)
        if translations.count() == 0 and \
           character.character.character.translated_from():
            translations = character.character.character.translated_from()\
                                              .translations(language)
        if translations.count() == 1:
            character.character = translations.get()\
                                              .official_name()
            new_character = StoryCharacterRevision.clone(
              character,
              story_revision.changeset,
              fork=True,
              story_revision=story_revision)
            for group in new_character.group.all():
                new_character.group.remove(group)
            if new_character.group_name.exists():
                for group_name in new_character.group_name.all():
                    new_character.group_name.remove(group_name)
                    translations = group_name.group.translations(
                        language)
                    if translations.count() == 0 and \
                       group_name.group.translated_from():
                        translations = group_name.group\
                                                 .translated_from()\
                                                 .translations(language)
                    if translations.count() == 1:
                        new_character.group_name.add(
                            translations.get().official_name())
                    else:
                        new_character.group_universe = None
                        new_character.save()
            return new_character
        return None

    def show_character_notes(self):
        from apps.gcd.models.story import character_notes
        return character_notes(self)

    def __str__(self):
        if hasattr(self, 'character'):
            return "%s: %s" % (self.story_revision, self.character)
        else:
            return "%s: None" % (self.story_revision,)
    ######################################
    # TODO old methods, t.b.c

    _base_field_list = ['character', 'role', 'universe',
                        'group_name', 'group_universe',
                        'is_flashback', 'is_origin', 'is_death', 'notes']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'character': None,
            'role': None,
            'group_name': None,
            'is_flashback': False,
            'is_origin': False,
            'is_death': False,
            'notes': '',
            'universe': None,
            'group_universe': None,
        }

    def show_notes(self):
        from apps.gcd.models.story import character_notes
        return character_notes(self)

    def _imps_for(self, field_name):
        # imps already come from StoryRevision, since is_changed is True there
        return 0


class CharacterOrderRevision(Revision):
    class Meta:
        app_label = 'oi'
        db_table = 'oi_character_order_revision'

    character_order = models.ForeignKey(CharacterOrder, null=True,
                                        on_delete=models.CASCADE,
                                        related_name='revisions')
    character_revisions = models.ManyToManyField(
      StoryCharacterRevision, through='CharacterThroughOrderRevision')
    story_revision = models.ForeignKey(
      'StoryRevision', on_delete=models.CASCADE,
      related_name='character_order_revisions')
    type = models.ForeignKey(CharacterOrderType,
                             on_delete=models.CASCADE)

    source_name = 'character_order'
    source_class = CharacterOrder

    @property
    def source(self):
        return self.character_order

    @source.setter
    def source(self, value):
        self.character_order = value

    def _pre_save_object(self, changes):
        self.character_order.story = self.story_revision.story

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        self.story_revision = kwargs['story_revision']

    def _post_save_object(self, changes):
        characters = self.character_order.characters.all()
        character_revisions = self.character_revisions.all()
        for character in characters:
            if not character_revisions.filter(
              character__id=character.id,
              universe=character.universe).count():
                self.character_order.characters.remove(character)
            else:
                character.order_code = character_revisions.get(
                  character__id=character.id,
                  universe=character.universe).order_code
                character.save()
        for character_revision in character_revisions:
            if not characters.filter(
              id=character_revision.character.id,
              universe=character_revision.universe).exists():
                order_code = character_revision\
                  .characterthroughorderrevision_set.get(order=self).order_code
                self.character_order.characters.add(
                  character_revision.story_character,
                  through_defaults={'order_code': order_code})

    @property
    def ordered_characters(self):
        return self.character_revisions.order_by(
          'characterthroughorderrevision__order_code')

    def story_characters(self):
        # get existing characters in their order
        order = 0
        character_order_list = []
        for character in self.ordered_characters:
            character_order_list.append((character, order))
            order += 1
        character_order_list.append((None, order))
        order += 1
        # get all characters appearing in the story
        # user order by id, which could reflect creation order
        story_characters = self.story_revision.appearing_characters\
                               .order_by('id')
        # process characters to have civilians after their aliases
        character_list = _order_civilian_after_alias(story_characters)
        for character in character_list:
            character_id = character[0].id
            # add characters to the list if not already present in the order
            if not self.character_revisions.filter(id=character_id).exists():
                character_order_list.append((character[0], order))
                order += 1
                # we do not add civilians if their alias is present, so
                # we ignore character[1] here
        return character_order_list

    def _get_blank_values(self):
        return {
            'story_revision': None,
            'type': None,
        }

    def process_ordered_appearing_characters(self):
        from apps.gcd.models.story import process_ordered_appearing_characters
        self.story = self.story_revision
        return process_ordered_appearing_characters(self)

    def __str__(self):
        return "%s: (order: %s)" % (self.story_revision, self.type)


class CharacterThroughOrderRevision(models.Model):
    class Meta:
        app_label = 'oi'
        db_table = 'oi_character_through_order'
        ordering = ['order_code']

    order = models.ForeignKey(CharacterOrderRevision,
                              on_delete=models.CASCADE)
    story_character = models.ForeignKey(StoryCharacterRevision,
                                        on_delete=models.CASCADE)
    order_code = models.IntegerField(default=0, db_index=True)


class StoryGroupRevision(Revision):
    class Meta:
        db_table = 'oi_story_group_revision'
        ordering = ['group_name__sort_name']

    story_group = models.ForeignKey(StoryGroup, null=True,
                                    on_delete=models.CASCADE,
                                    related_name='revisions')

    group = models.ForeignKey(Group, null=True, blank=True,
                              on_delete=models.CASCADE,
                              related_name='story_group_revisions')
    group_name = models.ForeignKey(GroupNameDetail, null=True,
                                   on_delete=models.CASCADE)
    universe = models.ForeignKey(Universe, null=True, blank=True,
                                 on_delete=models.CASCADE)
    story_revision = models.ForeignKey(
      'StoryRevision', on_delete=models.CASCADE,
      related_name='story_group_revisions')
    notes = models.TextField(blank=True)

    source_name = 'story_group'
    source_class = StoryGroup

    @property
    def source(self):
        return self.story_group

    @source.setter
    def source(self, value):
        self.story_group = value

    def _pre_save_object(self, changes):
        self.story_group.story = self.story_revision.story

    def _do_complete_added_revision(self, story_revision):
        self.story_revision = story_revision

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        self.story_revision = kwargs['story_revision']

    def __str__(self):
        return "%s: %s" % (self.story_revision, self.group)

    ######################################
    # TODO old methods, t.b.c

    _base_field_list = ['group_name', 'universe', 'notes']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'group_name': None,
            'universe': None,
            'notes': '',
        }

    def _imps_for(self, field_name):
        # imps already come from StoryRevision, since is_changed is True there
        return 0


class StoryArcRevision(Revision):
    class Meta:
        db_table = 'oi_story_arc_revision'
        ordering = ['-created', '-id']

    story_arc = models.ForeignKey(StoryArc, on_delete=models.CASCADE,
                                  null=True, related_name='revisions')
    name = models.CharField(max_length=255)
    leading_article = models.BooleanField(default=False)
    disambiguation = models.CharField(
      max_length=255, default='', db_index=True, blank=True,
      help_text='If needed a short phrase for the disambiguation of '
                'story arcs with a similar or identical name.')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    year_first_published = models.IntegerField(db_index=True, blank=True,
                                               null=True)
    year_first_published_uncertain = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    source_name = 'story_arc'
    source_class = StoryArc

    @property
    def source(self):
        return self.story_arc

    @source.setter
    def source(self, value):
        self.story_arc = value

    _base_field_list = ['name', 'leading_article', 'disambiguation',
                        'language', 'year_first_published',
                        'year_first_published_uncertain',
                        'description', 'notes',]

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'name': '',
            'leading_article': False,
            'disambiguation': '',
            'language': None,
            'year_first_published': None,
            'year_first_published_uncertain': False,
            'description': '',
            'notes': '',
        }

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        if fork is False:
            value = self.story_arc.name != self.story_arc.sort_name
            self.leading_article = value

    def _post_assign_fields(self, changes):
        if self.leading_article:
            self.story_arc.sort_name = remove_leading_article(self.name)
        else:
            self.story_arc.sort_name = self.name

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

    def get_absolute_url(self):
        if self.story_arc is None:
            return "/story_arc/revision/%i/preview" % self.id
        return self.story_arc.get_absolute_url()

    def _queue_name(self):
        return self.__str__()

    def __str__(self):
        return '%s (%s)' % (self.name, self.language.code.upper())


class StoryArcRelationRevision(Revision):
    """
    Relations between story arcs.
    """

    class Meta:
        db_table = 'oi_story_arc_relation_revision'
        ordering = ('to_story_arc', 'relation_type', 'from_story_arc')
        verbose_name_plural = 'Story Arc Relation Revisions'

    story_arc_relation = models.ForeignKey('gcd.StoryArcRelation',
                                           on_delete=models.CASCADE,
                                           null=True,
                                           related_name='revisions')

    to_story_arc = models.ForeignKey('gcd.StoryArc',
                                     on_delete=models.CASCADE,
                                     related_name='to_story_arc_revisions')
    relation_type = models.ForeignKey('gcd.StoryArcRelationType',
                                      on_delete=models.CASCADE,
                                      related_name='revisions')
    from_story_arc = models.ForeignKey('gcd.StoryArc',
                                       on_delete=models.CASCADE,
                                       related_name='from_story_arc_revisions')
    notes = models.TextField(blank=True)

    _base_field_list = ['from_story_arc', 'relation_type', 'to_story_arc',
                        'notes']

    def _field_list(self):
        field_list = self._base_field_list
        return field_list

    def _get_blank_values(self):
        return {
            'from_story_arc': None,
            'to_story_arc': None,
            'relation_type': None,
            'notes': ''
        }

    source_name = 'story_arc_relation'
    source_class = StoryArcRelation

    @property
    def source(self):
        return self.story_arc_relation

    @source.setter
    def source(self, value):
        self.story_arc_relation = value

    def _get_source(self):
        return self.story_arc_relation

    def _get_source_name(self):
        return 'story_arc_relation'

    def _imps_for(self, field_name):
        return 1

    def _pre_delete(self, changes):
        for revision in self.source.revisions.all():
            setattr(revision, 'story_arc_relation_id', None)
            revision.save()
        self.story_arc_relation_id = None

    def __str__(self):
        return '%s >%s< %s' % (str(self.from_story_arc),
                               str(self.relation_type),
                               str(self.to_story_arc)
                               )


def _order_civilian_after_alias(story_characters):
    character_list = []
    for character in story_characters:
        alias_identity = set(
            character.character.character.from_related_character
                     .filter(relation_type__id=2)
                     .values_list('from_character', flat=True))\
                     .intersection(story_characters.filter(
                                   universe=character.universe).values_list(
                                   'character__character', flat=True))
        if alias_identity:
            continue
        civilian_identity = _get_civilian_identity(character,
                                                   story_characters)
        if civilian_identity:
            civilian_identity = story_characters.filter(
                universe=character.universe,
                character__character__id__in=civilian_identity)
        character_list.append([character, civilian_identity])
    return character_list


class StoryRevision(Revision):
    class Meta:
        db_table = 'oi_story_revision'
        ordering = ['-created', '-id']

    story = models.ForeignKey(Story, on_delete=models.CASCADE, null=True,
                              related_name='revisions')

    title = models.CharField(max_length=255, blank=True)
    title_inferred = models.BooleanField(default=False)
    first_line = models.CharField(max_length=255, blank=True)
    feature = models.CharField(max_length=255, blank=True)
    feature_object = models.ManyToManyField(Feature, blank=True)
    feature_logo = models.ManyToManyField(FeatureLogo, blank=True)
    story_arc = models.ManyToManyField(StoryArc, blank=True)
    universe = models.ManyToManyField(Universe, blank=True)
    type = models.ForeignKey(StoryType, on_delete=models.CASCADE)
    sequence_number = models.IntegerField()

    page_count = models.DecimalField(max_digits=10, decimal_places=3,
                                     null=True, blank=True)
    page_count_uncertain = models.BooleanField(default=False)

    script = models.TextField(blank=True)
    pencils = models.TextField(blank=True)
    inks = models.TextField(blank=True)
    colors = models.TextField(blank=True)
    letters = models.TextField(blank=True)
    editing = models.TextField(blank=True)

    no_script = models.BooleanField(default=False)
    no_pencils = models.BooleanField(default=False)
    no_inks = models.BooleanField(default=False)
    no_colors = models.BooleanField(default=False)
    no_letters = models.BooleanField(default=False)
    no_editing = models.BooleanField(default=False)

    job_number = models.CharField(max_length=25, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    characters = models.TextField(blank=True)
    synopsis = models.TextField(blank=True)
    reprint_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    keywords = models.TextField(blank=True, default='')

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True,
                              related_name='story_revisions')
    date_inferred = models.BooleanField(default=False)

    source_name = 'story'
    source_class = Story

    @property
    def source(self):
        return self.story

    @source.setter
    def source(self, value):
        self.story = value

    @classmethod
    def _get_stats_category_field_tuples(cls):
        return frozenset({('issue', 'series', 'country',),
                          ('issue', 'series', 'language',)})

    def _pre_delete(self, changes):
        # sigh, some people add story_credits to be deleted stories
        for revision in self.story_credit_revisions.all():
            if revision.added:
                revision.delete()

    @classmethod
    def copied_revision(cls, story, changeset, issue_revision,
                        copy_credit_info=False,
                        copy_characters=False):
        """
        Given an existing story, create a new revision based on it for a
        new story with the copied data. 'fork' is set to true in such a case.
        """
        revision = StoryRevision.clone(story, changeset, fork=True)
        revision.issue = issue_revision.issue
        revision.sequence_number = issue_revision.next_sequence_number()
        if revision.type.id == STORY_TYPES['cover']:
            if revision.changeset.storyrevisions.filter(
              issue=revision.issue,
              type__id=STORY_TYPES['cover'],
              deleted=False).exists():
                revision.type = StoryType.objects.get(
                  name='cover reprint (on interior page)')
        credits = story.active_credits
        if revision.issue.series.language != story.issue.series.language:
            if revision.letters:
                revision.letters = '?'
            revision.title = ''
            revision.title_inferred = False
            revision.first_line = ''
            credits = credits.exclude(credit_type_id=CREDIT_TYPES['letters'])
            revision.feature_logo.clear()
            for feature_object in revision.feature_object.all():
                # TODO this works for now, but make consistent with
                # StoryCharacterRevision.copied_translation and
                # extend to StoryArcs
                # in particular, use .translations(language)
                translations = feature_object.translations().filter(
                  to_feature__language=revision.issue.series.language)
                if translations.count() == 1:
                    # revision is a translation from original
                    revision.feature_object.add(translations.get().to_feature)
                elif (translations.count() == 0 and
                      feature_object.translated_from() is not None):
                    translated_from = feature_object.translated_from()
                    if translated_from.language == \
                       revision.issue.series.language:
                        # revision is the source of a translation
                        revision.feature_object.add(translated_from)
                    else:
                        other_translations = feature_object.translated_from()\
                                                           .translations()\
                                                           .filter(
                          to_feature__language=revision.issue.series.language)
                        if other_translations.count() == 1:
                            # revision is a translation from another language
                            revision.feature_object.add(
                              other_translations.get().to_feature)
                revision.feature_object.remove(feature_object)
            for story_arc in revision.story_arc.all():
                # translations = story_arc.get_translations_in_language(
                #   revision.issue.series.language)
                # if translations.count() == 1:
                #     revision.story_arc.add(translations.get())
                revision.story_arc.remove(story_arc)

        if not copy_characters:
            revision.characters = ''
        revision.save()
        if copy_credit_info:
            exclude = {'is_sourced', 'sourced_by'}
        else:
            exclude = {'is_credited', 'credited_as', 'is_signed', 'signed_as',
                       'signature', 'is_sourced', 'sourced_by', 'credit_name'}
        for credit in credits:
            StoryCreditRevision.clone(credit, revision.changeset,
                                      fork=True, story_revision=revision,
                                      exclude=exclude)
        if copy_characters:
            characters = []
            if issue_revision.series.language == story.issue.series.language:
                same_language = True
            else:
                same_language = False
            for character in story.active_characters:
                if same_language:
                    StoryCharacterRevision.clone(character,
                                                 revision.changeset,
                                                 fork=True,
                                                 story_revision=revision)
                else:
                    translated = StoryCharacterRevision.copied_translation(
                      character, revision)
                    if translated is None:
                        characters.append(character.character.character.name)
                        if character.role:
                            characters[-1] += ' (%s)' % character.role.name
            if characters:
                if revision.characters:
                    characters.append(revision.characters)
                revision.characters = '; '.join(characters)
                revision.save()

            for group in story.active_groups:
                if same_language:
                    StoryGroupRevision.clone(group,
                                             revision.changeset,
                                             fork=True,
                                             story_revision=revision)
                else:
                    translations = group.group_name.group.translations(
                      issue_revision.series.language)
                    if translations.count() == 0 and \
                       group.group_name.group.translated_from():
                        translations = group.group_name.group\
                                            .translated_from()\
                                            .translations(issue_revision
                                                          .series.language)

                    if translations.count() == 1:
                        group.group_name = translations.get().official_name()
                        StoryGroupRevision.clone(
                          group, revision.changeset, fork=True,
                          story_revision=revision)
        return revision

    @classmethod
    def clone_revision(cls, story_revision, changeset, issue_revision,
                       copy_credit_info=False,
                       copy_characters=False):
        """
        Given an existing story revision of the changeset, create a new
        revision based on it for a new story with the copied data.
        'fork' is set to true in such a case.
        """
        new_revision = StoryRevision.clone(story_revision, changeset,
                                           fork=True, exclude={'keywords'})
        new_revision.issue = issue_revision.issue
        new_revision.sequence_number = issue_revision.next_sequence_number()
        new_revision.save()
        credits = story_revision.story_credit_revisions.filter(deleted=False)
        if copy_credit_info:
            exclude = {'is_sourced', 'sourced_by'}
        else:
            exclude = {'is_credited', 'credited_as', 'is_signed', 'signed_as',
                       'signature', 'is_sourced', 'sourced_by', 'credit_name'}
        for credit in credits:
            StoryCreditRevision.clone(credit, changeset,
                                      fork=True, story_revision=new_revision,
                                      exclude=exclude)
        if copy_characters:
            for character in story_revision.story_character_revisions.filter(
              deleted=False):
                StoryCharacterRevision.clone(character, changeset, fork=True,
                                             story_revision=new_revision)

            for group in story_revision.story_group_revisions.filter(
              deleted=False):
                StoryGroupRevision.clone(group, changeset, fork=True,
                                         story_revision=new_revision)
        else:
            new_revision.characters = ''
            new_revision.save()
        return new_revision

    def _get_major_changes(self, extra_field_tuples=frozenset()):
        # We need to look at issue for index status changes, but it does
        # not otherwise behave like a normal parent field, nor does it
        # fit into any of the other unusual field classifications.
        extras = {('issue',)}

        if extra_field_tuples:
            # extra_field_tuples might be a frozenset, so add to our new
            # set rather than the other way around.
            extras.add(extra_field_tuples)

        return super(StoryRevision, self)._get_major_changes(
            extra_field_tuples=extras)

    def compare_changes(self, compare_revision=None):
        super(StoryRevision, self).compare_changes(
          compare_revision=compare_revision)
        for credit_type in CREDIT_TYPES:
            if not self.deleted and not self.changed[credit_type]:
                credits = self.story_credit_revisions.filter(
                               credit_type__name=credit_type)
                if not compare_revision:
                    compare_revision = self.previous()
                if not credits and compare_revision and \
                    compare_revision.story_credit_revisions.filter(
                      credit_type_id=CREDIT_TYPES[credit_type]).exists():
                    self.changed[credit_type] = True
                    self.is_changed = True
                elif credits:
                    if compare_revision == self.previous():
                        for credit in credits:
                            credit.compare_changes()
                            if credit.is_changed:
                                self.changed[credit_type] = True
                                self.is_changed = True
                                break
                    else:
                        # fall back to text comparison since no
                        # credit_revisions correspond
                        from apps.gcd.templatetags.credits import \
                          show_creator_credit
                        self_story = PreviewStory.init(self)
                        self_credit_text = show_creator_credit(self_story,
                                                               credit_type,
                                                               url=False)
                        compare_story = PreviewStory.init(compare_revision)
                        compare_revision_credit_text = show_creator_credit(
                          compare_story, credit_type, url=False)
                        if self_credit_text != compare_revision_credit_text:
                            self.changed[credit_type] = True
                            self.is_changed = True

        if 'characters' not in self.changed or not self.changed['characters']:
            for story_character in self.story_character_revisions.all():
                story_character.compare_changes()
                if story_character.is_changed:
                    self.changed['characters'] = True
                    self.is_changed = True
                    break

        if 'characters' not in self.changed or not self.changed['characters']:
            for story_group in self.story_group_revisions.all():
                story_group.compare_changes()
                if story_group.is_changed:
                    self.changed['characters'] = True
                    self.is_changed = True
                    break

        if 'genre' in self.changed and self.changed['genre'] \
           and self.previous():
            if self.previous().genre.lower() == self.genre.lower():
                self.changed['genre'] = False

        if 'genre' not in self.changed or not self.changed['genre']:
            if 'feature_object' in self.changed and \
              self.changed['feature_object']:
                from apps.oi.templatetags.compare import _compare_string_genre
                if self.previous():
                    previous = _compare_string_genre(self.previous())
                else:
                    previous = ''
                current = _compare_string_genre(self)
                if previous != current:
                    self.changed['genre'] = True

    def _do_complete_added_revision(self, issue):
        """
        Do the necessary processing to complete the fields of a new
        story revision for adding a record before it can be saved.
        """
        self.issue = issue

    def _reset_values(self):
        # TODO: undo StoryCredit and StoryCharacter changes
        # TODO: remove added StoryCredit, StoryCharacter
        # and StoryGroup revisions
        if self.deleted:
            # users can edit story revisions before deleting them.
            # ensure that the final deleted revision matches the
            # final state of the story.
            self.title = self.story.title
            self.title_inferred = self.story.title_inferred
            self.first_line = self.first_line
            self.feature = self.story.feature
            self.page_count = self.story.page_count
            self.page_count_uncertain = self.story.page_count_uncertain

            self.script = self.story.script
            self.pencils = self.story.pencils
            self.inks = self.story.inks
            self.colors = self.story.colors
            self.letters = self.story.letters
            self.editing = self.story.editing

            self.no_script = self.story.no_script
            self.no_pencils = self.story.no_pencils
            self.no_inks = self.story.no_inks
            self.no_colors = self.story.no_colors
            self.no_letters = self.story.no_letters
            self.no_editing = self.story.no_editing

            self.notes = self.story.notes
            self.synopsis = self.story.synopsis
            self.characters = self.story.characters
            self.reprint_notes = self.story.reprint_notes
            self.genre = self.story.genre
            self.type = self.story.type
            self.job_number = self.story.job_number
            self.sequence_number = self.story.sequence_number
            self.save()

    def _post_m2m_add(self, fork=False, fork_source=None, exclude=frozenset()):
        # fields of BiblioEntry need to be handled separately
        if self.type.id == STORY_TYPES['about comics']:
            biblio_revision = BiblioEntryRevision(storyrevision_ptr=self)
            # need to copy everything
            biblio_revision.__dict__.update(self.__dict__)
            source_story = biblio_revision.source
            if fork is True:
                source_story = fork_source
            # copy single value fields which are specific to biblio_entry
            keys = biblio_revision._get_single_value_fields().keys()
            subtract_keys = biblio_revision.storyrevision_ptr\
                                           ._get_single_value_fields().keys()
            for field in keys - subtract_keys:
                if hasattr(source_story, "biblioentry"):
                    value = getattr(source_story.biblioentry, field)
                else:
                    value = getattr(source_story.biblioentryrevision, field)
                setattr(biblio_revision, field, value)
            biblio_revision.save()

    def _handle_dependents(self, changes):
        # fields of BiblioEntry need to be handled separately
        if self.type.id == STORY_TYPES['about comics']:
            if not hasattr(self.source, 'biblioentry'):
                biblio_entry = BiblioEntry(story_ptr=self.source)
                biblio_entry.__dict__.update(self.source.__dict__)
                biblio_entry.save()
                self.biblioentryrevision.save()
            self.biblioentryrevision._copy_fields_to(
              self.biblioentryrevision.source.biblioentry)
            self.biblioentryrevision.source.biblioentry.save()
        elif hasattr(self.source, 'biblioentry'):
            # former BiblioEntry, delete add-on type
            super(GcdData, self.biblioentryrevision.source.biblioentry)\
                  .delete(keep_parents=True)

        # While committing an issue is a prerequisite for the story,
        # accounting for index status changes is dependent upon the
        # story commit.
        issues = [] if self.added else [changes['old issue']]
        if changes['issue changed'] and not self.deleted:
            issues.append(changes['new issue'])

        # import pytest
        for issue in issues:
            delta = issue.set_indexed_status()
            if delta:
                if self.edited:
                    assert issue.series.country is not None
                    assert issue.series.language is not None
                CountStats.objects.update_all_counts(
                    {'issue indexes': delta},
                    country=issue.series.country,
                    language=issue.series.language)
            # this is done for every story, but does not result in double
            # entries in RecentIndexedIssue, check is in update_recents
            #
            # maybe can be done using changes[] on the changeset level ?
            if issue.is_indexed and not issue.variant_of:
                RecentIndexedIssue.objects.update_recents(issue)

    def extra_forms(self, request):
        from apps.oi.forms.story import StoryRevisionFormSet, \
                                        StoryCharacterRevisionFormSet, \
                                        StoryGroupRevisionFormSet
        credits_formset = StoryRevisionFormSet(
          request.POST or None,
          instance=self,
          queryset=self.story_credit_revisions.filter(deleted=False))

        story_characters = self.story_character_revisions.filter(deleted=False)
        character_list = _order_civilian_after_alias(story_characters)
        order = 0
        # Create a dict to store order by character id
        order_map = {}
        for character in character_list:
            order_map[character[0].id] = order
            order += 1
            if character[1]:
                for ci in character[1]:
                    order_map[ci.id] = order
                    order += 1
        story_characters.order_map = order_map

        characters_formset = StoryCharacterRevisionFormSet(
          request.POST or None,
          instance=self,
          queryset=story_characters)

        groups_formset = StoryGroupRevisionFormSet(
          request.POST or None,
          instance=self,
          queryset=self.story_group_revisions.filter(deleted=False))
        return {'credits_formset': credits_formset,
                'characters_formset': characters_formset,
                'groups_formset': groups_formset}

    @classmethod
    def extra_forms_errors(cls, request, form, extra_forms):
        credits_formset = extra_forms['credits_formset']
        if not credits_formset.is_valid() and request.user.indexer.use_tabs:
            form.add_error(None, "Changes needed on the Creators tab.")

        characters_formset = extra_forms['characters_formset']
        if not characters_formset.is_valid() and request.user.indexer.use_tabs:
            form.add_error(None, "Changes needed on the Characters tab.")

        groups_formset = extra_forms['groups_formset']
        if not groups_formset.is_valid() and request.user.indexer.use_tabs:
            form.add_error(None, "Changes needed on the Characters tab.")

    def process_extra_forms(self, extra_forms):
        credits_formset = extra_forms['credits_formset']
        # TODO use _process_formset, but need to handle additional logic
        for credit_form in credits_formset:
            if credit_form.is_valid() and credit_form.cleaned_data \
               and credit_form not in credits_formset.deleted_forms:
                cd = credit_form.cleaned_data
                if 'id' in cd and cd['id']:
                    credit_revision = credit_form.save()
                else:
                    credit_revision = credit_form.save(commit=False)
                    credit_revision.save_added_revision(
                      changeset=self.changeset, story_revision=self)
                if credit_revision.credit_type.id in [7, 8, 9, 10, 11,
                                                      12, 13, 14]:
                    if credit_revision.credit_type.id == 9:
                        credit_revision.credit_name = 'painting'
                    credit_revision.credit_type = CreditType.objects.get(id=2)
                    credit_revision.save()
                    credit_revision.id = None
                    credit_revision.previous_revision = None
                    credit_revision.source = None
                    credit_revision.credit_type = CreditType.objects.get(id=3)
                    credit_revision.save()
                    if cd['credit_type'].id in [8, 9, 11, 13]:
                        credit_revision.id = None
                        credit_revision.previous_revision = None
                        credit_revision.source = None
                        credit_revision.credit_type = CreditType.objects.get(
                          id=4)
                        credit_revision.save()
                    if cd['credit_type'].id in [10, 11, 12, 13]:
                        credit_revision.id = None
                        credit_revision.previous_revision = None
                        credit_revision.source = None
                        credit_revision.credit_type = CreditType.objects.get(
                          id=1)
                        credit_revision.save()
                    if cd['credit_type'].id in [12, 13, 14]:
                        credit_revision.id = None
                        credit_revision.previous_revision = None
                        credit_revision.source = None
                        credit_revision.credit_type = \
                            CreditType.objects.get(id=5)
                        credit_revision.save()
            elif (not credit_form.is_valid() and
                  credit_form not in credits_formset.deleted_forms):
                raise ValueError
        removed_credits = credits_formset.deleted_forms
        if removed_credits:
            _removed_related_objects(removed_credits, 'story_credit')
        characters_formset = extra_forms['characters_formset']
        # TODO use _process_formset, but need to handle additional logic
        for character_form in characters_formset:
            if character_form.is_valid() and character_form.cleaned_data \
               and character_form not in characters_formset.deleted_forms:
                cd = character_form.cleaned_data
                if 'id' in cd and cd['id']:
                    character_revision = character_form.save()
                else:
                    character_revision = character_form.save(commit=False)
                    character_revision.save_added_revision(
                      changeset=self.changeset, story_revision=self)
                    character_form.save_m2m()
                # Change this, if we ever edit character appearances elsewhere
                if character_revision.group_name.exists() and \
                   character_revision.universe and not \
                   character_revision.group_universe:
                    character_revision.group_universe = \
                      character_revision.universe
                    character_revision.save()
            elif (not character_form.is_valid() and
                  character_form not in characters_formset.deleted_forms):
                raise ValueError
        removed_characters = characters_formset.deleted_forms
        if removed_characters:
            _removed_related_objects(removed_characters, 'story_character')
        groups_formset = extra_forms['groups_formset']
        _process_formset(self, groups_formset, revision_type='story_revision')
        removed_groups = groups_formset.deleted_forms
        if removed_groups:
            _removed_related_objects(removed_groups, 'story_group')

    def post_form_save(self):
        if self.feature_logo.count():
            # stories for variants in variant-add next to issue have issue
            if self.issue:
                language = self.issue.series.language
            else:
                language = self.my_issue_revision.\
                                other_issue_revision.series.language
            for feature_logo in self.feature_logo.all():
                if feature_logo.feature.get(language=language) not in \
                  self.feature_object.all():
                    self.feature_object.add(feature_logo.feature.
                                            get(language=language))
        if self.story_character_revisions.count():
            for story_character in self.story_character_revisions.all():
                # no processing for deleted appearances
                if story_character.deleted:
                    continue
                # make sure groups with the group universe exist for each
                # character appearance that has a group
                if story_character.group_name.count():
                    for group_name in story_character.group_name.all():
                        story_group = self.story_group_revisions.filter(
                          group_name=group_name,
                          universe=story_character.group_universe,
                          deleted=False)
                        if not story_group.exists():
                            story_group = StoryGroupRevision.objects.create(
                              group_name=group_name,
                              universe=story_character.group_universe,
                              story_revision=self,
                              changeset=self.changeset)
                # Check if a superhero has a unique civilian identity.
                if story_character.character.character.to_related_character\
                                  .filter(relation_type__id=2).count() == 1:
                    # Check if a superhero has a civilian identity entered.
                    # If not, add the official name of the civilian identity
                    character_identity = story_character.character.character\
                      .to_related_character.filter(relation_type__id=2).get()\
                      .to_character
                    if not self.story_character_revisions\
                               .filter(
                                 universe=story_character.universe,
                                 character__character=character_identity)\
                               .exists():
                        # civilian identities are not in a superhero group, so
                        # we don't need to copy this data via adds
                        # need to reset some fields not to be copied
                        story_character.pk = None
                        story_character._state.adding = True
                        story_character.previous_revision_id = None
                        story_character.source = None
                        story_character.character = character_identity\
                                       .character_names.get(
                                         is_official_name=True)
                        story_character.group_universe = None
                        story_character.notes = ''
                        story_character.save()
            # check for extra groups with same universe added
            for story_group in self.story_group_revisions\
                                   .filter(deleted=False,
                                           notes='',
                                           story_group_id=None):
                other_group_rev = self.story_group_revisions.filter(
                  group_name=story_group.group_name,
                  universe=story_group.universe,
                  deleted=False)\
                  .exclude(id=story_group.id)
                if other_group_rev.exists():
                    story_group.delete()

    def old_credits(self):
        for credit_type in ('script', 'pencils', 'inks', 'colors', 'letters',
                            'editing'):
            credit = getattr(self, credit_type)
            if credit:
                for s in credit.split(";"):
                    stripped = s.strip()
                    if not stripped.startswith('?') \
                       and stripped not in ['various', 'typeset', 'gesetzt',
                                            'tryckstil', 'formatadas',
                                            'typographie', 'Maschinenschrift',
                                            'composición tipográfica',
                                            'dattiloscritto']:
                        return True
        return False

    def migrate_credits(self):
        for credit_type in ('script', 'pencils', 'inks', 'colors', 'letters',
                            'editing'):
            if getattr(self, credit_type) and \
              getattr(self, credit_type) != '?':
                credits = getattr(self, credit_type).strip(';')
                credits = credits.split(';')
                old_credits = ''
                for credit in credits:
                    credit = credit.strip()
                    if credit in ['Typeset', 'Computer']:
                        credit = 'typeset'
                    save_credit = credit
                    credit = credit.replace('  ', ' ')
                    if credit[-1] == '?':
                        credit = credit[:-1]
                        uncertain = True
                    else:
                        uncertain = False
                    is_credited = False
                    credited_as = ''
                    signed_as = ''
                    is_signed = False
                    ghost_possible = False
                    if credit.find('(') > 1:
                        note = credit[credit.find('(')+1:].strip()
                        end_note = note.find(')')
                        remainder_note = note[end_note+1:].strip()
                        note = note[:end_note].strip()
                        save_credit = credit
                        credit = credit[:credit.find('(')-1].strip()
                        if credit[-1] == '?':
                            credit = credit[:-1].strip()
                            uncertain = True
                        if note in ['credited', 'kreditert']:
                            is_credited = True
                            note = ''
                            if remainder_note:
                                if remainder_note.find('as ') > 1:
                                    credited_as = remainder_note[
                                                  remainder_note.find('as ')+3:
                                                  remainder_note.find(']')]
                                else:
                                    note = remainder_note
                        elif note in ['signed', 'signert', 'signiert']:
                            is_signed = True
                            note = ''
                            if remainder_note:
                                if remainder_note.find('as ') > 1:
                                    signed_as = remainder_note[
                                                remainder_note.find('as ') + 3:
                                                remainder_note.find(']')]
                                else:
                                    note = remainder_note
                        elif note == 'painted':
                            note = 'painting'
                        elif (note == 'signed, credited' or
                              note == 'credited, signed'):
                            is_signed = True
                            is_credited = True
                            note = ''
                        elif (note == 'signed, painted' or
                              note == 'painted, signed'):
                            is_signed = True
                            note = 'painting'
                        else:
                            note = save_credit[save_credit.find('('):].strip()
                    else:
                        note = ''
                    if credit.find('[') > 1:
                        value = credit[credit.find('[')+1:]
                        value = value[value.find(' ')+1:]
                        value = value.strip().strip(']')
                        if is_signed:
                            signed_as = value
                            credit = credit[:credit.find('[')-1]
                        else:
                            credit = value
                            ghost_possible = True
                    creator = CreatorNameDetail.objects.filter(name=credit,
                                                               deleted=False)
                    if not ghost_possible:
                        # exclude ghost names
                        creator = creator.exclude(type=12)

                    if creator.count() == 1:
                        creator = creator.get()
                        if uncertain and not creator.is_official_name:
                            if creator.in_script == creator.creator\
                               .active_names().get(is_official_name=True)\
                               .in_script:
                                creator = creator.creator.active_names().get(
                                                  is_official_name=True)
                        if note and note[0] == '(' and note[-1] == ')':
                            note = note[1:-1]
                        credit_revision = StoryCreditRevision(
                          changeset=self.changeset,
                          story_revision_id=self.id,
                          creator=creator,
                          credit_type_id=CREDIT_TYPES[credit_type],
                          is_credited=is_credited,
                          credited_as=credited_as,
                          is_signed=is_signed,
                          signed_as=signed_as,
                          uncertain=uncertain,
                          credit_name=note)
                        credit_revision.save()
                    else:
                        if old_credits:
                            old_credits += '; ' + save_credit
                        else:
                            old_credits = save_credit
                setattr(self, credit_type, old_credits)
                self.save()

    def migrate_single_feature(self, feature):
        from apps.select.views import FeatureAutocomplete
        if self.issue:
            series = self.issue.series
        else:
            series = self.changeset.issuerevisions.get(issue=None).series
        self.forwarded = {'language_code': series.language.code,
                          'type': self.type_id}
        self.q = feature
        feature_object = FeatureAutocomplete.get_queryset(
          self, interactive=False)
        if feature_object.count() > 1:
            feature_object = feature_object.filter(name=feature)
        if feature_object.count() == 1:
            self.feature_object.add(feature_object.get())
            return True
        if feature_object.count() == 0:
            self.forwarded = {'type': self.type_id}
            feature_object = FeatureAutocomplete.get_queryset(
              self, interactive=False)
            if feature_object.count() == 1:
                feature_other_language = feature_object.get()
                translations = feature_other_language.translations().filter(
                  to_feature__language=series.language)
                if translations.count() == 1:
                    self.feature_object.add(translations.get().to_feature)
                    return True
        return False

    def migrate_feature(self):
        if self.feature:
            features = self.feature.split(';')
            old_features = ''
            for feature in features:
                feature = feature.strip()
                save_feature = feature
                feature = feature.replace('  ', ' ')
                migrated = self.migrate_single_feature(feature)
                if not migrated and feature.find('[') > 1:
                    feature = feature[:feature.find('[')]
                    feature = feature.strip()
                    migrated = self.migrate_single_feature(feature)
                if not migrated:
                    if old_features:
                        old_features += '; ' + save_feature
                    else:
                        old_features = save_feature
            setattr(self, 'feature', old_features)
            self.save()

    def deletable(self):
        if self.changeset.reprintrevisions \
                         .filter(origin=self.story).count() \
                or self.changeset.reprintrevisions \
                                 .filter(target=self.story).count() \
                or (self.story and self.story.has_reprints(notes=False)):
            return False
        else:
            return True

    def toggle_deleted(self):
        """
        Mark this revision as deleted, meaning that instead of copying it
        back to the display table, the display table entry will be removed
        when the revision is committed.
        """
        self.deleted = not self.deleted
        if bool(self.story_credit_revisions.all()):
            for story_credit_revision in self.story_credit_revisions.all():
                story_credit_revision.deleted = self.deleted
                story_credit_revision.save()
        if bool(self.story_character_revisions.all()):
            for story_character_revision in self.story_character_revisions\
                                                .all():
                story_character_revision.deleted = self.deleted
                story_character_revision.save()
        self.save()

    def get_absolute_url(self):
        if self.story is None:
            return "/issue/revision/%i/preview/#%i" % (
                self.my_issue_revision.id, self.id)
        return self.story.get_absolute_url()

    def has_feature(self):
        """
        feature_logo entry automatically results in corresponding
        feature_object entry, therefore no check needed
        """
        return self.feature or self.feature_object.count()

    @property
    def appearing_characters(self):
        return self.story_character_revisions.exclude(deleted=True)

    @property
    def active_characters(self):
        return self.story_character_revisions.exclude(deleted=True)

    @property
    def active_groups(self):
        return self.story_group_revisions.exclude(deleted=True)

    def show_characters(self, url=True, css_style=True, compare=False):
        return show_characters(self, url=url, css_style=css_style,
                               compare=compare)

    def show_feature(self):
        return show_feature(self)

    def show_feature_as_text(self):
        return show_feature_as_text(self)

    def show_title(self, use_first_line=False):
        return show_title(self, use_first_line)

    def __str__(self):
        """
        Re-implement locally instead of using self.story because it may change.
        """
        from apps.gcd.templatetags.display import show_story_short
        return show_story_short(self, no_number=True, markup=False)

    ######################################
    # TODO old methods, t.b.c.

    @property
    def my_issue_revision(self):
        if not hasattr(self, '_saved_my_issue_revision'):
            self._saved_my_issue_revision = \
                self.changeset.issuerevisions.filter(issue=self.issue)[0]
        return self._saved_my_issue_revision

    def moveable(self):
        """
        A story revision is moveable
        a) if it is not currently attached to an issue and is a revision of a
           previously existing story. Therefore it is a story which was moved
           to the version issue, this way it can be moved back.
        b) an issue version of mine in this changeset has no story attached and
           it is a cover sequence. Therefore one cover sequence can be moved
           from the base to the version issue.

        These conditions work for our current only case of a story move: i.e.
        issue versions.
        """
        if self.changeset.change_type == CTYPES['variant_add'] or \
           self.changeset.change_type == CTYPES['two_issues']:
            if self.issue is None:
                if self.story is None:
                    return False
                return True

            if self.deleted:
                return False

            if self.my_issue_revision.other_issue_revision.variant_of \
               is not None:
                # variants can only have one sequence, and it needs to be cover
                if self.changeset.storyrevisions \
                                 .exclude(issue=self.issue).count() \
                        or self.type != StoryType.objects.get(name='Cover'):
                    return False
                else:
                    return True
            return True
        else:
            return False

    def _field_list(self):
        fields = get_story_field_list()
        if self.previous() and (self.previous().issue_id != self.issue_id):
            fields = ['issue'] + fields
        return fields

    def _get_blank_values(self):
        return {
            'title': '',
            'title_inferred': False,
            'first_line': '',
            'feature': '',
            'feature_object': None,
            'feature_logo': None,
            'story_arc': None,
            'page_count': None,
            'page_count_uncertain': False,
            'script': '',
            'pencils': '',
            'inks': '',
            'colors': '',
            'letters': '',
            'editing': '',
            'no_script': False,
            'no_pencils': False,
            'no_inks': False,
            'no_colors': False,
            'no_letters': False,
            'no_editing': True,
            'notes': '',
            'keywords': '',
            'synopsis': '',
            'universe': None,
            'characters': '',
            'reprint_notes': '',
            'genre': '',
            'type': None,
            'job_number': '',
            'sequence_number': None,
            'issue': None,
        }

    def calculate_imps(self):
        imps = super(StoryRevision, self).calculate_imps()
        if hasattr(self, 'biblioentryrevision'):
            imps += self.biblioentryrevision.calculate_imps()
        return imps

    def _start_imp_sum(self):
        self._seen_script = False
        self._seen_pencils = False
        self._seen_inks = False
        self._seen_colors = False
        self._seen_letters = False
        self._seen_editing = False
        self._seen_page_count = False
        self._seen_title = False
        self._seen_feature = False

    def _imps_for(self, field_name):
        if field_name in ('first_line', 'type', 'universe', 'story_arc',
                          'characters', 'synopsis', 'job_number',
                          'reprint_notes', 'notes', 'keywords', 'issue'):
            return 1
        if field_name == 'genre':
            if not self.story:
                return 1
            if self.story.genre.find(';') > 0:
                old_genre = self.story.genre.lower().split("; ")
                old_genre.sort()
                old_genre = "; ".join(old_genre)
            else:
                old_genre = self.story.genre.lower()
            if self.genre.lower() != old_genre:
                return 1
            else:
                return 0

        if not self._seen_feature and field_name in ('feature',
                                                     'feature_object',
                                                     'feature_logo'):
            self._seen_feature = True
            return 1

        if not self._seen_title and field_name in ('title', 'title_inferred'):
            self._seen_title = True
            return 1

        if not self._seen_page_count and \
           field_name in ('page_count', 'page_count_uncertain'):
            self._seen_page_count = True
            if field_name == 'page_count':
                return 1

            # checking the 'uncertain' box  without also at least guessing
            # the page count itself doesn't count as IMP-worthy information.
            if field_name == 'page_count_uncertain' and \
               self.page_count is not None:
                return 1

        for name in ('script', 'pencils', 'inks', 'colors',
                     'letters', 'editing'):
            attr = '_seen_%s' % name
            no_name = 'no_%s' % name
            if not getattr(self, attr) and field_name in (name, no_name):
                setattr(self, attr, True)

                # Just putting in a question mark isn't worth an IMP.
                # Note that the input data is already whitespace-stripped.
                # Changed StoryCredits give also positive is_changed and
                # therefore corresponding IMP here.
                if field_name == name and getattr(self, field_name) == '?':
                    if self.story_credit_revisions.exists() == 0:
                        return 0
                return 1
        return 0

    # we need two checks if relevant reprint revisions exist:
    # 1) revisions which are active and link self.story with a story/issue
    #    in the current direction under consideration
    # 2) existing reprints which are locked and which link self.story
    #    with a story/issue in the current direction under consideration
    # if this is the case we return reprintrevisions and not reprint links
    # returned reprint links are three cases:
    # a) revisions in the current changeset which link self.story with a
    #    story/issue in the current direction under consideration
    # b) newly added and active revisions in other changesets
    #    we do not need .exclude(changeset__id=self.changeset_id)\ the new
    #    ones from the current changeset we want anyway
    # c) for the current corresponding reprint links the latest revisions
    #    which are not in the current changeset, the latest can be fetched
    #    via next_revision=None, that way we get either approved or
    #    active ones

    # for newly added stories it is easy, just show reprintrevision which
    # point to the new story in the right ways

    def old_revisions_base(self):
        revs = ReprintRevision.objects \
                              .exclude(changeset__id=self.changeset_id)\
                              .exclude(changeset__state=states.DISCARDED)
        return revs

    def from_reprints_oi(self, preview=False):
        if self.story is None:
            return self.target_reprint_revisions\
                       .filter(changeset__id=self.changeset_id)
        from_reprints = self.story.from_reprints.all()
        from_reprints_ids = from_reprints.values_list('id', flat=True)
        if self.story.target_reprint_revisions.active_set().count() \
                or RevisionLock.objects.filter(
                  changeset=self.changeset,
                  object_id__in=from_reprints_ids).exists():
            # reprint revisions of the story that are currently in
            # active changesets
            new_revisions = self.story.target_reprint_revisions.active_set()
            if preview:
                # new reprint revisions of story that are in other active
                # changesets are not shown in preview, neither are deleted ones
                new_revisions = new_revisions.exclude(deleted=True)\
                                .filter(changeset__id=self.changeset_id)

            new_revisions_ids = new_revisions.values_list('id', flat=True)
            if not preview:
                # reprint revisions of story that represent current state,
                # but which are not edited in this changeset,
                old_revisions = self.story.target_reprint_revisions\
                        .filter(next_revision=None)\
                        .exclude(changeset__id=self.changeset_id)\
                        .exclude(changeset__state=states.DISCARDED) \
                        .exclude(deleted=True)
                # reprint revisions of story that are edited in
                # other active changesets
                next_revisions_ids = self.story.target_reprint_revisions\
                    .exclude(next_revision=None)\
                    .exclude(next_revision__changeset__id=self.changeset_id)\
                    .filter(next_revision__changeset__state__in=states.ACTIVE)\
                    .values_list('next_revision__id', flat=True)
            else:
                # revisions of story that are not currently not being edited
                old_revisions = self.story.target_reprint_revisions\
                        .filter(next_revision=None,
                                changeset__state=states.APPROVED) \
                        .exclude(deleted=True)
                next_revisions_ids = []
            old_revisions_ids = old_revisions.values_list('id', flat=True)
            revisions_ids = set(new_revisions_ids) | set(old_revisions_ids) | \
                set(next_revisions_ids)
            return ReprintRevision.objects.filter(id__in=revisions_ids)
        else:
            return from_reprints

    @property
    def from_all_reprints(self):
        return self.from_reprints_oi(preview=True)

    def from_story_reprints_oi(self, preview=False):
        return self.from_reprints_oi(preview=preview).exclude(origin=None)

    @property
    def from_story_reprints(self):
        return self.from_reprints_oi(preview=True)

    def from_issue_reprints_oi(self, preview=False):
        return self.from_reprints_oi(preview=preview).filter(origin=None)

    @property
    def from_issue_reprints(self):
        return self.from_issue_reprints_oi(preview=True)

    def to_reprints_oi(self, preview=False):
        if self.story is None:
            return self.origin_reprint_revisions\
                       .filter(changeset__id=self.changeset_id)
        to_reprints = self.story.to_reprints.all()
        to_reprints_ids = to_reprints.values_list('id', flat=True)
        if self.story.origin_reprint_revisions.active_set().count() \
                or RevisionLock.objects.filter(
                  changeset=self.changeset,
                  object_id__in=to_reprints_ids).exists():
            # reprint revisions of the story that are currently in
            # active changesets
            new_revisions = self.story.origin_reprint_revisions.active_set()
            if preview:
                # new reprint revisions of story that are in other active
                # changesets are not shown in preview, neither are deleted ones
                new_revisions = new_revisions.exclude(deleted=True)\
                                .filter(changeset__id=self.changeset_id)

            new_revisions_ids = new_revisions.values_list('id', flat=True)

            if not preview:
                # reprint revisions of story that represent current state,
                # but which are not edited in this changeset,
                old_revisions = self.story.origin_reprint_revisions\
                        .filter(next_revision=None)\
                        .exclude(changeset__id=self.changeset_id)\
                        .exclude(changeset__state=states.DISCARDED) \
                        .exclude(deleted=True)
                # reprint revisions of story that are edited in
                # other active changesets
                next_revisions_ids = self.story.origin_reprint_revisions\
                    .exclude(next_revision=None)\
                    .exclude(next_revision__changeset__id=self.changeset_id)\
                    .filter(next_revision__changeset__state__in=states.ACTIVE)\
                    .values_list('next_revision__id', flat=True)
            else:
                # revisions of story that are not currently not being edited
                old_revisions = self.story.origin_reprint_revisions\
                        .filter(next_revision=None,
                                changeset__state=states.APPROVED) \
                        .exclude(deleted=True)
                next_revisions_ids = []
            old_revisions_ids = old_revisions.values_list('id', flat=True)
            revisions_ids = set(new_revisions_ids) | set(old_revisions_ids) | \
                set(next_revisions_ids)
            return ReprintRevision.objects.filter(id__in=revisions_ids)
        else:
            return to_reprints

    @property
    def to_all_reprints(self):
        return self.to_reprints_oi(preview=True)

    def to_story_reprints_oi(self, preview=False):
        return self.to_reprints_oi(preview=preview).exclude(target=None)

    @property
    def to_story_reprints(self):
        return self.to_story_reprints_oi(preview=True)

    def to_issue_reprints_oi(self, preview=False):
        return self.to_reprints_oi(preview=preview).filter(target=None)

    @property
    def to_issue_reprints(self):
        return self.to_issue_reprints_oi(preview=True)

    def has_reprint_revisions(self):
        if self.story is None:
            if self.target_reprint_revisions\
                   .filter(changeset__id=self.changeset_id).count():
                return True
            elif self.origin_reprint_revisions\
                     .filter(changeset__id=self.changeset_id).count():
                return True
            else:
                return False
        if self.story.target_reprint_revisions\
               .filter(changeset__id=self.changeset_id).count():
            return True
        if self.story.origin_reprint_revisions\
               .filter(changeset__id=self.changeset_id).count():
            return True
        if self.story.to_reprints\
               .filter(revisions__changeset=self.changeset)\
               .count():
            return True
        if self.story.from_reprints\
               .filter(revisions__changeset=self.changeset)\
               .count():
            return True
        return False


class PreviewStory(Story):
    class Meta:
        proxy = True

    @classmethod
    def init(cls, story_revision):
        preview_story = PreviewStory()
        story_revision._copy_fields_to(preview_story)
        preview_story.keywords = story_revision.keywords
        preview_story.revision = story_revision
        preview_story.id = story_revision.id
        return preview_story

    @property
    def feature_object(self):
        return self.revision.feature_object.exclude(deleted=True)

    @property
    def story_arc(self):
        return self.revision.story_arc.all()

    @property
    def credits(self):
        return self.revision.story_credit_revisions.exclude(deleted=True)

    @property
    def active_credits(self):
        return self.revision.story_credit_revisions.exclude(deleted=True)

    @property
    def active_characters(self):
        return self.revision.story_character_revisions.exclude(deleted=True)

    @property
    def active_groups(self):
        return self.revision.story_group_revisions.exclude(deleted=True)

    @property
    def character_orders(self):
        return self.revision.character_order_revisions.exclude(deleted=True)

    def has_credits(self):
        """
        Simplifies UI checks for conditionals.  Credit fields.
        """
        return (self.script or
                self.pencils or
                self.inks or
                self.colors or
                self.letters or
                self.editing or
                self.active_credits.exists())

    def has_content(self):
        """
        Simplifies UI checks for conditionals.  Content fields
        """
        return self.job_number or \
            self.genre or \
            self.has_characters() or \
            self.first_line or \
            self.synopsis or \
            self.has_keywords() or \
            self.has_reprints() or \
            self.feature_object.exclude(genre='').values('genre').exists() or \
            self.revision.feature_logo.count() or \
            self.active_awards().count()

    @property
    def from_all_reprints(self):
        return self.revision.from_reprints_oi(preview=True)

    @property
    def from_issue_reprints(self):
        return self.revision.from_issue_reprints_oi(preview=True)

    @property
    def from_story_reprints(self):
        return self.revision.from_story_reprints_oi(preview=True)

    @property
    def to_all_reprints(self):
        return self.revision.to_reprints_oi(preview=True)

    @property
    def to_issue_reprints(self):
        return self.revision.to_issue_reprints_oi(preview=True)

    @property
    def to_story_reprints(self):
        return self.revision.to_story_reprints_oi(preview=True)

    def has_keywords(self):
        return self.revision.has_keywords()

    @property
    def appearing_characters(self):
        return self.revision.story_character_revisions.exclude(deleted=True)

    def has_characters(self):
        return self.revision.characters or \
          self.revision.story_character_revisions.exclude(deleted=True)

    def show_characters(self):
        return self._show_characters(self)

    @property
    def universe(self):
        return self.revision.universe.all()

    def has_feature(self):
        return self.revision.feature or self.revision.feature_object.count()

    def show_feature_logo(self):
        return self._show_feature_logo(self.revision)

    @property
    def biblioentry(self):
        if hasattr(self.revision, 'biblioentryrevision'):
            return self.revision.biblioentryrevision
        else:
            return None


class BiblioEntryRevision(StoryRevision):
    class Meta:
        db_table = 'oi_biblio_entry_revision'
        ordering = ['-created', '-id']

    objects = RevisionManager()

    page_began = models.IntegerField(null=True, blank=True)
    page_ended = models.IntegerField(null=True, blank=True)
    abstract = models.TextField(blank=True)
    doi = models.TextField(blank=True)

    source_name = 'biblio_entry'
    source_class = BiblioEntry

    _regular_fields = None

    # otherwise the StoryRevision-routine is called
    def extra_forms(self, request):
        return {}

    def process_extra_forms(self, extra_forms):
        pass

    def previous(self):
        previous = super(StoryRevision, self).previous()
        if previous and hasattr(previous, 'biblioentryrevision'):
            return previous.biblioentryrevision
        else:
            return None

    def _field_list(self):
        fields = ['page_began', 'page_ended', 'abstract', 'doi']
        # TODO after python 3 and OrderedDict, this might work
        # fields += list(self._get_single_value_fields()
        # .viewkeys() -
        # self.storyrevision_ptr._get_single_value_fields().viewkeys())
        return fields

    def _imps_for(self, field_name):
        return 1

    def calculate_imps(self):
        imps = super(StoryRevision, self).calculate_imps()
        return imps

    def _get_blank_values(self):
        return {
            'page_began': None,
            'page_ended': None,
            'abstract': '',
            'doi': '',
        }

    def compare_changes(self):
        if self.type.id != STORY_TYPES['about comics']:
            self.deleted = True

        return super(StoryRevision, self).compare_changes()


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


class UniverseRevision(Revision):
    class Meta:
        db_table = 'oi_universe_revision'
        ordering = ['created', '-id']

    universe = models.ForeignKey('gcd.Universe',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 related_name='revisions')

    multiverse = models.CharField(max_length=255, db_index=True, blank=True)
    verse = models.ForeignKey(Multiverse, on_delete=models.CASCADE,
                              null=True)
    name = models.CharField(max_length=255, db_index=True, blank=True)
    designation = models.CharField(max_length=255, db_index=True, blank=True)

    year_first_published = models.IntegerField(db_index=True, null=True,
                                               blank=True)
    year_first_published_uncertain = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    source_name = 'universe'
    source_class = Universe

    @property
    def source(self):
        return self.universe

    @source.setter
    def source(self, value):
        self.universe = value

    _base_field_list = ['multiverse', 'verse', 'name', 'designation',
                        'year_first_published',
                        'year_first_published_uncertain',
                        'description', 'notes']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'multiverse': '',
            'verse': None,
            'name': '',
            'designation': '',
            'year_first_published': None,
            'year_first_published_uncertain': False,
            'description': '',
            'notes': '',
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
        return '%s: %s - %s (%s)' % (self.multiverse, self.name,
                                     self.designation,
                                     self.year_first_published)

    def get_absolute_url(self):
        if self.universe is None:
            return "/universe/revision/%i/preview" % self.id
        return self.universe.get_absolute_url()

    def __str__(self):
        return '%s: %s - %s' % (self.multiverse, self.name, self.designation)


class PreviewUniverse(Universe):
    class Meta:
        proxy = True


class CharacterGroupRevisionBase(Revision):
    class Meta:
        abstract = True

    name = models.CharField(max_length=255, db_index=True)
    sort_name = models.CharField(max_length=255, default='')
    disambiguation = models.CharField(
      max_length=255, db_index=True, blank=True,
      help_text='if needed add a short phrase for disambiguation')

    year_first_published = models.IntegerField(db_index=True, null=True,
                                               blank=True)
    year_first_published_uncertain = models.BooleanField(default=False)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    description = models.TextField(
      blank=True,
      help_text='concise description, including background and premise')
    notes = models.TextField(blank=True)
    keywords = models.TextField(blank=True, default='')

    def __str__(self):
        return '%s' % (self.name)

    ######################################
    # TODO old methods, t.b.c

    _base_field_list = ['disambiguation',
                        'year_first_published',
                        'year_first_published_uncertain', 'language',
                        'description', 'notes', 'keywords']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'name': '',
            'sort_name': '',
            'disambiguation': '',
            'language': None,
            'year_first_published': None,
            'year_first_published_uncertain': False,
            'universe': None,
            'description': '',
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


class CharacterRevision(CharacterGroupRevisionBase):
    class Meta:
        db_table = 'oi_character_revision'
        ordering = ['created', '-id']

    character = models.ForeignKey('gcd.Character',
                                  on_delete=models.CASCADE,
                                  null=True,
                                  related_name='revisions')
    universe = models.ForeignKey('gcd.Universe', on_delete=models.CASCADE,
                                 null=True, blank=True,
                                 related_name='character_revisions')
    external_link_revisions = GenericRelation(ExternalLinkRevision)

    source_name = 'character'
    source_class = Character

    _base_field_list = ['disambiguation',
                        'universe',
                        'year_first_published',
                        'year_first_published_uncertain', 'language',
                        'description', 'notes', 'keywords']

    @classmethod
    def _get_deprecated_field_names(cls):
        return frozenset({'universe'})

    @property
    def source(self):
        return self.character

    @source.setter
    def source(self, value):
        self.character = value

    def _do_create_dependent_revisions(self, delete=False):
        name_details = self.character.active_names()
        for name_detail in name_details:
            name_lock = _get_revision_lock(name_detail,
                                           changeset=self.changeset)
            if name_lock is None:
                raise IntegrityError("needed Name lock not possible")
            character_name = CharacterNameDetailRevision.clone(name_detail,
                                                               self.changeset)
            character_name.save_added_revision(changeset=self.changeset,
                                               character_revision=self)

            if delete:
                character_name.deleted = True
                character_name.save()
        if delete:
            for group_membership in self.character.active_memberships():
                membership_lock = _get_revision_lock(group_membership,
                                                     changeset=self.changeset)
                if membership_lock is None:
                    raise IntegrityError("needed GroupMembership lock not "
                                         "possible")
                group_membership_revision = \
                    GroupMembershipRevision.clone(group_membership,
                                                    self.changeset)
                group_membership_revision.deleted = True
                group_membership_revision.save()
            for character_relation in self.character.active_relations():
                relation_lock = _get_revision_lock(character_relation,
                                                   changeset=self.changeset)
                if relation_lock is None:
                    raise IntegrityError("needed CharacterRelation lock not "
                                         "possible")
                character_relation_revision = \
                    CharacterRelationRevision.clone(character_relation,
                                                    self.changeset)
                character_relation_revision.deleted = True
                character_relation_revision.save()


    def extra_forms(self, request):
        from apps.oi.forms import CharacterRevisionFormSet

        character_names_formset = CharacterRevisionFormSet(
          request.POST or None, instance=self,
          queryset=self.character_name_revisions.filter(deleted=False))

        external_link_formset = self._create_external_link_formset(request)

        return {'character_names_formset': character_names_formset,
                'external_link_formset': external_link_formset
                }

    def process_extra_forms(self, extra_forms):
        character_names_formset = extra_forms['character_names_formset']
        # TODO use _process_formset, but needs to handle official name update
        removed_names = character_names_formset.deleted_forms
        for character_name_form in character_names_formset:
            if character_name_form.is_valid() and \
               character_name_form.cleaned_data and \
               character_name_form not in removed_names:
                cd = character_name_form.cleaned_data
                if 'id' in cd and cd['id']:
                    character_revision = character_name_form.save()
                else:
                    character_revision = character_name_form.save(commit=False)
                    character_revision.save_added_revision(
                      changeset=self.changeset, character_revision=self)
                if cd['is_official_name']:
                    self.name = cd['name']
                    self.save()
            elif (
              not character_name_form.is_valid() and
              character_name_form not in character_names_formset.deleted_forms
            ):
                raise ValueError

        if removed_names:
            _removed_related_objects(removed_names, 'character_name_detail')

        self._process_external_link_formset(extra_forms)

    def _pre_save_object(self, changes):
        name = self.changeset.characternamedetailrevisions\
                             .get(is_official_name=True)
        self.character.name = name.name
        self.character.sort_name = name.sort_name

    def _handle_dependents(self, changes):
        # for new a character, we need to save the record_id in the
        # name revisions
        if self.added:
            for name in self.changeset.characternamedetailrevisions.all():
                name.creator = self.character
                name.save()

    def get_absolute_url(self):
        if self.character is None:
            return "/character/revision/%i/preview" % self.id
        return self.character.get_absolute_url()


class PreviewCharacter(Character):
    class Meta:
        proxy = True

    @property
    def official_name(self):
        return self.revision.character_name_revisions.get(
          is_official_name=True)

    def has_keywords(self):
        return self.revision.has_keywords()

    def display_keywords(self):
        return self.revision.keywords


class CharacterNameDetailRevision(Revision):
    """
    record of the character's name
    """

    class Meta:
        db_table = 'oi_character_name_detail_revision'
        ordering = ['sort_name', ]
        verbose_name_plural = 'Character Name Detail Revisions'

    character_name_detail = models.ForeignKey('gcd.CharacterNameDetail',
                                              on_delete=models.CASCADE,
                                              null=True,
                                              related_name='revisions')
    character_revision = models.ForeignKey(
      CharacterRevision,
      on_delete=models.CASCADE,
      related_name='character_name_revisions',
      null=True)
    character = models.ForeignKey(Character, on_delete=models.CASCADE,
                                  related_name='name_revisions', null=True)
    name = models.CharField(max_length=255, db_index=True)
    sort_name = models.CharField(max_length=255, default='')
    is_official_name = models.BooleanField(default=False)

    source_name = 'character_name_detail'
    source_class = CharacterNameDetail

    @property
    def source(self):
        return self.character_name_detail

    @source.setter
    def source(self, value):
        self.character_name_detail = value

    def _do_complete_added_revision(self, character_revision):
        self.character_revision = character_revision

    def _post_create_for_add(self, changes):
        self.character = self.character_revision.character

    def __str__(self):
        return '%s - %s' % (
            str(self.character), str(self.name))

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['name', 'sort_name', 'is_official_name']

    def _field_list(self):
        # for some reason, if we use self._base_field_list an additional
        # field 'character_revision' gets added, but don't know where and why.
        return ['name', 'sort_name', 'is_official_name']

    def _get_blank_values(self):
        return {
            'name': '',
            'sort_name': '',
            'is_official_name': False,
        }

    def _imps_for(self, field_name):
        if field_name == 'sort_name':
            if self.sort_name == self.name:
                return 0
            else:
                return 1
        if field_name in self._field_list():
            return 1
        return 0


class CharacterRelationRevision(Revision):
    """
    Relations between characters.
    """

    class Meta:
        db_table = 'oi_character_relation_revision'
        ordering = ('to_character', 'relation_type', 'from_character')
        verbose_name_plural = 'Character Relation Revisions'

    character_relation = models.ForeignKey('gcd.CharacterRelation',
                                           on_delete=models.CASCADE,
                                           null=True,
                                           related_name='revisions')

    to_character = models.ForeignKey('gcd.Character', on_delete=models.CASCADE,
                                     related_name='to_character_revisions')
    relation_type = models.ForeignKey('gcd.CharacterRelationType',
                                      on_delete=models.CASCADE,
                                      related_name='revisions')
    from_character = models.ForeignKey('gcd.Character',
                                       on_delete=models.CASCADE,
                                       related_name='from_character_revisions')
    notes = models.TextField(blank=True)

    source_name = 'character_relation'
    source_class = CharacterRelation

    @property
    def source(self):
        return self.character_relation

    @source.setter
    def source(self, value):
        self.character_relation = value

    def _pre_delete(self, changes):
        for revision in self.source.revisions.all():
            setattr(revision, 'character_relation_id', None)
            revision.save()
        self.character_relation_id = None

    _base_field_list = ['from_character', 'relation_type', 'to_character',
                        'notes']

    def _field_list(self):
        field_list = self._base_field_list
        return field_list

    def _get_blank_values(self):
        return {
            'from_character': None,
            'to_character': None,
            'relation_type': None,
            'notes': ''
        }

    def _imps_for(self, field_name):
        return 1

    def __str__(self):
        return '%s >%s< %s' % (str(self.from_character),
                               str(self.relation_type),
                               str(self.to_character)
                               )


class GroupRevision(CharacterGroupRevisionBase):
    class Meta:
        db_table = 'oi_group_revision'
        ordering = ['created', '-id']

    _base_field_list = ['disambiguation', 'universe',
                        'year_first_published',
                        'year_first_published_uncertain', 'language',
                        'description', 'notes', 'keywords']

    group = models.ForeignKey('gcd.Group',
                              on_delete=models.CASCADE,
                              null=True,
                              related_name='revisions')
    universe = models.ForeignKey('gcd.Universe', on_delete=models.CASCADE,
                                 null=True, blank=True,
                                 related_name='group_revisions')

    source_name = 'group'
    source_class = Group

    @classmethod
    def _get_deprecated_field_names(cls):
        return frozenset({'universe'})

    @property
    def source(self):
        return self.group

    @source.setter
    def source(self, value):
        self.group = value

    def _do_create_dependent_revisions(self, delete=False):
        name_details = self.group.active_names()
        for name_detail in name_details:
            name_lock = _get_revision_lock(name_detail,
                                           changeset=self.changeset)
            if name_lock is None:
                raise IntegrityError("needed Name lock not possible")
            group_name = GroupNameDetailRevision.clone(name_detail,
                                                       self.changeset)
            group_name.save_added_revision(changeset=self.changeset,
                                           group_revision=self)

            if delete:
                group_name.deleted = True
                group_name.save()

    def extra_forms(self, request):
        from apps.oi.forms import GroupRevisionFormSet
        # from apps.oi.forms.support import CREATOR_HELP_LINKS

        group_names_formset = GroupRevisionFormSet(
          request.POST or None, instance=self,
          queryset=self.group_name_revisions.filter(deleted=False))

        return {'group_names_formset': group_names_formset,
                }

    def process_extra_forms(self, extra_forms):
        group_names_formset = extra_forms['group_names_formset']
        # TODO use _process_formset, but needs to handle official name update
        for group_name_form in group_names_formset:
            if group_name_form.is_valid() and \
               group_name_form.cleaned_data and \
               group_name_form not in group_names_formset.deleted_forms:
                cd = group_name_form.cleaned_data
                if 'id' in cd and cd['id']:
                    group_revision = group_name_form.save()
                else:
                    group_revision = group_name_form.save(commit=False)
                    group_revision.save_added_revision(
                      changeset=self.changeset, group_revision=self)
                if cd['is_official_name']:
                    self.name = cd['name']
                    self.save()
            elif (
              not group_name_form.is_valid() and
              group_name_form not in group_names_formset.deleted_forms
            ):
                raise ValueError

        removed_names = group_names_formset.deleted_forms
        if removed_names:
            _removed_related_objects(removed_names, 'group_name_detail')

    def _pre_save_object(self, changes):
        name = self.changeset.groupnamedetailrevisions\
                             .get(is_official_name=True)
        self.group.name = name.name
        self.group.sort_name = name.sort_name

    def _handle_dependents(self, changes):
        # for new group, we need to save the record_id in the name revisions
        if self.added:
            for name in self.changeset.groupnamedetailrevisions.all():
                name.group = self.group
                name.save()

    def get_absolute_url(self):
        if self.group is None:
            return "/group/revision/%i/preview" % self.id
        return self.group.get_absolute_url()


class GroupNameDetailRevision(Revision):
    """
    record of the group's name
    """

    class Meta:
        db_table = 'oi_group_name_detail_revision'
        ordering = ['sort_name', ]
        verbose_name_plural = 'Group Name Detail Revisions'

    group_name_detail = models.ForeignKey('gcd.GroupNameDetail',
                                          on_delete=models.CASCADE,
                                          null=True,
                                          related_name='revisions')
    group_revision = models.ForeignKey(
      GroupRevision,
      on_delete=models.CASCADE,
      related_name='group_name_revisions',
      null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              related_name='name_revisions', null=True)
    name = models.CharField(max_length=255, db_index=True)
    sort_name = models.CharField(max_length=255, default='')
    is_official_name = models.BooleanField(default=False)

    source_name = 'group_name_detail'
    source_class = GroupNameDetail

    @property
    def source(self):
        return self.group_name_detail

    @source.setter
    def source(self, value):
        self.group_name_detail = value

    def _do_complete_added_revision(self, group_revision):
        self.group_revision = group_revision

    def _post_create_for_add(self, changes):
        self.group = self.group_revision.group

    def __str__(self):
        return '%s - %s' % (
            str(self.group), str(self.name))

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['name', 'sort_name', 'is_official_name']

    def _field_list(self):
        # for some reason, if we use self._base_field_list an additional
        # field 'character_revision' gets added, but don't know where and why.
        return ['name', 'sort_name', 'is_official_name']

    def _get_blank_values(self):
        return {
            'name': '',
            'sort_name': '',
            'is_official_name': False,
        }

    def _imps_for(self, field_name):
        if field_name == 'sort_name':
            if self.sort_name == self.name:
                return 0
            else:
                return 1
        if field_name in self._field_list():
            return 1
        return 0


class GroupRelationRevision(Revision):
    """
    Relations between groups.
    """

    class Meta:
        db_table = 'oi_group_relation_revision'
        ordering = ('to_group', 'relation_type', 'from_group')
        verbose_name_plural = 'Group Relation Revisions'

    group_relation = models.ForeignKey('gcd.GroupRelation',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       related_name='revisions')

    to_group = models.ForeignKey('gcd.Group', on_delete=models.CASCADE,
                                 related_name='to_group_revisions')
    relation_type = models.ForeignKey('gcd.GroupRelationType',
                                      on_delete=models.CASCADE,
                                      related_name='revisions')
    from_group = models.ForeignKey('gcd.Group', on_delete=models.CASCADE,
                                   related_name='from_group_revisions')
    notes = models.TextField(blank=True)

    source_name = 'group_relation'
    source_class = GroupRelation

    @property
    def source(self):
        return self.group_relation

    @source.setter
    def source(self, value):
        self.group_relation = value

    def _pre_delete(self, changes):
        for revision in self.source.revisions.all():
            setattr(revision, 'group_relation_id', None)
            revision.save()
        self.group_relation_id = None

    _base_field_list = ['from_group', 'relation_type', 'to_group',
                        'notes']

    def _field_list(self):
        field_list = self._base_field_list
        return field_list

    def _get_blank_values(self):
        return {
            'from_group': None,
            'to_group': None,
            'relation_type': None,
            'notes': ''
        }

    def _imps_for(self, field_name):
        return 1

    def __str__(self):
        return '%s >%s< %s' % (str(self.from_group),
                               str(self.relation_type),
                               str(self.to_group)
                               )


class GroupMembershipRevision(Revision):
    """
    record the group membership of character
    """

    class Meta:
        db_table = 'oi_group_membership_revision'
        ordering = ['created', '-id']
        verbose_name_plural = 'Character Group Membership Revisions'

    group_membership = models.ForeignKey('gcd.GroupMembership',
                                         on_delete=models.CASCADE,
                                         null=True,
                                         related_name='revisions')
    character = models.ForeignKey('gcd.character', on_delete=models.CASCADE,
                                  related_name='membership_revisions')
    group = models.ForeignKey('gcd.group', on_delete=models.CASCADE,
                              related_name='membership_revisions')
    organization_name = models.CharField(max_length=200)
    membership_type = models.ForeignKey('gcd.GroupMembershipType',
                                        on_delete=models.CASCADE)
    year_joined = models.PositiveSmallIntegerField(null=True, blank=True)
    year_joined_uncertain = models.BooleanField(default=False)
    year_left = models.PositiveSmallIntegerField(null=True, blank=True)
    year_left_uncertain = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    source_name = 'group_membership'
    source_class = GroupMembership

    @property
    def source(self):
        return self.group_membership

    @source.setter
    def source(self, value):
        self.group_membership = value

    def _pre_delete(self, changes):
        for revision in self.source.revisions.all():
            setattr(revision, 'group_membership_id', None)
            revision.save()
        self.group_membership_id = None

    def get_absolute_url(self):
        if self.group_membership is None:
            return "/group_membership/revision/%i/preview" % self.id
        return self.group_membership.get_absolute_url()

    def __str__(self):
        return '%s - %s' % (self.character, self.group)

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['character',
                        'group',
                        'membership_type',
                        'year_joined',
                        'year_joined_uncertain',
                        'year_left',
                        'year_left_uncertain',
                        'notes',
                        ]

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'character': None,
            'group': None,
            'membership_type': None,
            'year_joined': None,
            'year_joined_uncertain': False,
            'year_left': None,
            'year_left_uncertain': False,
            'notes': '',
        }

    def _start_imp_sum(self):
        self._seen_year_joined = False
        self._seen_year_left = False

    def _imps_for(self, field_name):
        if field_name in ('year_joined',
                          'year_joined_uncertain'):
            if not self._seen_year_joined:
                self._seen_year_joined = True
                return 1
        elif field_name in ('year_left',
                            'year_left_uncertain'):
            if not self._seen_year_left:
                self._seen_year_left = True
                return 1
        elif field_name in self._base_field_list:
            return 1
        return 0


def get_reprint_field_list():
    return ['notes']


class ReprintRevision(Revision):
    class Meta:
        db_table = 'oi_reprint_revision'
        ordering = ['-created', '-id']
        get_latest_by = "created"

    reprint = models.ForeignKey(Reprint, on_delete=models.CASCADE, null=True,
                                related_name='revisions')

    origin = models.ForeignKey(Story, on_delete=models.CASCADE,
                               null=True,
                               related_name='origin_reprint_revisions')
    origin_revision = models.ForeignKey(
      StoryRevision, on_delete=models.CASCADE, null=True,
      related_name='origin_reprint_revisions')

    origin_issue = models.ForeignKey(
      Issue, on_delete=models.CASCADE, null=True,
      related_name='origin_reprint_revisions')

    @property
    def origin_sort(self):
        if self.origin_issue:
            if self.origin_issue.key_date:
                sort = self.origin_issue.key_date
            else:
                sort = '9999-99-99'
            return "%s-%d-%d" % (sort, self.origin_issue.series.year_began,
                                 self.origin_issue.sort_code)
        else:
            if self.origin.issue.key_date:
                sort = self.origin.issue.key_date
            else:
                sort = '9999-99-99'
            return "%s-%d-%d" % (sort, self.origin.issue.series.year_began,
                                 self.origin.issue.sort_code)

    target = models.ForeignKey(Story, on_delete=models.CASCADE,
                               null=True,
                               related_name='target_reprint_revisions')
    target_revision = models.ForeignKey(
      StoryRevision, on_delete=models.CASCADE, null=True,
      related_name='target_reprint_revisions')

    target_issue = models.ForeignKey(Issue, on_delete=models.CASCADE,
                                     null=True,
                                     related_name='target_reprint_revisions')

    @property
    def target_sort(self):
        if self.target_issue:
            if self.target_issue.key_date:
                sort = self.target_issue.key_date
            else:
                sort = '9999-99-99'
            return "%s-%d-%d" % (sort, self.target_issue.series.year_began,
                                 self.target_issue.sort_code)
        else:
            if self.target.issue.key_date:
                sort = self.target.issue.key_date
            else:
                sort = '9999-99-99'
            return "%s-%d-%d" % (sort, self.target.issue.series.year_began,
                                 self.target.issue.sort_code)

    notes = models.TextField(max_length=255, default='')

    source_name = 'reprint'
    source_class = Reprint

    @property
    def source(self):
        return self.reprint

    @source.setter
    def source(self, value):
        self.reprint = value

    def _field_list(self):
        return ['origin', 'origin_revision', 'origin_issue',
                'target', 'target_revision', 'target_issue',
                'notes']

    def _get_blank_values(self):
        return {
            'origin': None,
            'origin_revision': None,
            'origin_issue': None,
            'target': None,
            'target_revision': None,
            'target_issue': None,
            'notes': '',
        }

    def _pre_delete(self, changes):
        for revision in self.source.revisions.all():
            setattr(revision, 'reprint_id', None)
            # origin/target sequence might have moved to another issue
            # after this change was approved
            if revision.origin and (revision.origin.issue !=
                                    revision.origin_issue):
                revision.origin_issue = revision.origin.issue
            if revision.target and (revision.target.issue !=
                                    revision.target_issue):
                revision.target_issue = revision.target.issue
            revision.save()
        self.reprint_id = None

    def _start_imp_sum(self):
        self._seen_origin = False
        self._seen_target = False

    def _imps_for(self, field_name):
        """
        All current reprint fields are simple one point fields.
        Only one point for changing origin issue to origin story, etc.
        """
        if field_name in ('origin', 'origin_revision',
                          'origin_issue'):
            if not self._seen_origin:
                self._seen_origin = True
                return 1
        if field_name in ('target', 'target_revision',
                          'target_issue'):
            if not self._seen_target:
                self._seen_target = True
                return 1
        if field_name == 'notes':
            return 1
        return 0

    def save(self, *args, **kwargs):
        # Ensure that we can't create a nonsense link.
        # Check first revisions since for sequence moves things get
        # complicated in view of the checks.
        if self.origin_revision:
            if self.origin and self.origin_revision.story != self.origin:
                raise ValueError(
                    "Reprint origin story revision and origin story do not "
                    "agree.  Story from revision: '%s'; Story: '%s'" %
                    (self.origin_revision.story, self.origin))

            if (self.origin_issue and
                    self.origin_revision.issue != self.origin_issue):
                raise ValueError(
                    "Reprint origin story revision issue and origin issue "
                    "do not agree.  Issue from revision: '%s'; Issue: '%s'" %
                    (self.origin_revision.issue, self.origin_issue))

        if self.target_revision:
            if self.target and self.target_revision.story != self.target:
                raise ValueError(
                    "Reprint target story revision and target story do not "
                    "agree.  Story from revision: '%s'; Story: '%s'" %
                    (self.target_revision.story, self.target))

            if (self.target_issue and
                    self.target_revision.issue != self.target_issue):
                raise ValueError(
                    "Reprint target story revision issue and target issue "
                    "do not agree.  Issue from revision: '%s'; Issue: '%s'" %
                    (self.target_revision.issue, self.target_issue))

        if self.origin:
            if self.origin_issue and self.origin_issue != self.origin.issue:
                raise ValueError(
                    "Reprint origin story and issue do not match.  Story "
                    "issue: '%d: %s'; Issue: '%d: %s'" % (self.origin.issue.id,
                                                          self.origin.issue,
                                                          self.origin_issue.id,
                                                          self.origin_issue))
            if not self.origin_issue:
                self.origin_issue = self.origin.issue

        if self.target:
            if self.target_issue and self.target_issue != self.target.issue:
                raise ValueError(
                    "Reprint target story and issue do not match.  Story "
                    "issue: '%d: %s'; Issue: '%d: %s'" % (self.target.issue.id,
                                                          self.target.issue,
                                                          self.target_issue.id,
                                                          self.target_issue))
            if not self.target_issue:
                self.target_issue = self.target.issue

        super(ReprintRevision, self).save(*args, **kwargs)

    def _pre_stats_measurement(self, changes):
        # If we have StoryRevisions instead of Stories, commit them
        # first and set our Story fields so that our own commit can
        # be handled generically after this point.
        if self.origin_revision:
            self.origin_revision.commit_to_display()
            self.origin = self.origin_revision.source
            self.origin_issue = self.origin.issue

        if self.target_revision:
            self.target_revision.commit_to_display()
            self.target = self.target_revision.source
            self.target_issue = self.target.issue

    def get_compare_string(self, base_issue, do_compare=False):
        moved = False
        if do_compare:
            self.compare_changes()
        if self.origin_issue == base_issue or \
           (self.origin_revision and self.origin_revision.issue == base_issue):
            direction = 'in'
            if do_compare and self.previous_revision:
                if 'origin_issue' in self.changed and \
                        self.changed['origin_issue']:
                    if self.origin_issue and \
                            self.origin_issue == \
                            self.previous_revision.target_issue:
                        moved = False
                    else:
                        moved = True
                elif 'origin' in self.changed and \
                        self.changed['origin']:
                    if self.origin and \
                            self.origin == \
                            self.previous_revision.target:
                        moved = False
                    else:
                        moved = True
            issue = self.target_issue
            if self.target:
                story = self.target
            elif self.target_revision:
                story = self.target_revision
            else:
                story = None
        else:
            direction = 'from'
            if do_compare and self.previous_revision:
                if 'target_issue' in self.changed and \
                        self.changed['target_issue']:
                    if self.target_issue and \
                            self.target_issue == \
                            self.previous_revision.origin_issue:
                        moved = False
                    else:
                        moved = True
                elif 'target' in self.changed and \
                        self.changed['target']:
                    if self.target and \
                            self.target == \
                            self.previous_revision.origin:
                        moved = False
                    else:
                        moved = True
            issue = self.origin_issue
            if self.origin:
                story = self.origin
            elif self.origin_revision:
                story = self.origin_revision
            else:
                story = None

        if story:
            reprint = '%s %s <br><i>sequence</i> ' \
                      '<a target="_blank" href="%s#%d">%s %s</a>' % \
                      (direction, esc(issue.full_name()),
                       issue.get_absolute_url(), story.id, esc(story),
                       show_title(story, True))
        else:
            reprint = '%s <a target="_blank" href="%s">%s</a>' % \
                      (direction, issue.get_absolute_url(),
                       esc(issue.full_name()))
        if self.notes:
            reprint = '%s [%s]' % (reprint, esc(self.notes))
        if moved:
            from apps.gcd.templatetags.display import show_story_short
            if self.previous_revision.target_issue == base_issue or \
               self.previous_revision.origin_issue == base_issue:
                reprint += '<br>reprint link was moved from issue'
            elif self.previous_revision.target and \
                    self.previous_revision.target.issue == base_issue:
                reprint += \
                    '<br>reprint link was moved from %s]' % \
                    show_story_short(self.previous_revision.target)
            else:
                reprint += \
                    '<br>reprint link was moved from %s]' % \
                    show_story_short(self.previous_revision.origin)
        return mark_safe(reprint)

    def _handle_prerequisites(self, changes):
        if self.origin_revision:
            self.origin = self.origin_revision.story
            self.origin_issue = self.origin.issue
        if self.target_revision:
            self.target = self.target_revision.story
            self.target_issue = self.target.issue

    def __str__(self):
        if self.origin or self.origin_revision:
            if self.origin:
                origin = self.origin
            else:
                origin = self.origin_revision
            reprint = '%s %s of %s ' % (
                origin, show_title(origin, True), origin.issue)
        else:
            reprint = '%s ' % (self.origin_issue)
        if self.target or self.target_revision:
            if self.target:
                target = self.target
            else:
                target = self.target_revision
            reprint += 'reprinted in %s %s of %s' % (
                target, show_title(target, True), target.issue)
        else:
            reprint += 'reprinted in %s' % (self.target_issue)
        if self.notes:
            reprint = '%s [%s]' % (reprint, esc(self.notes))
        if self.deleted:
            reprint += ' [DELETED]'
        return mark_safe(reprint)


class ImageRevisionManager(RevisionManager):

    def clone_revision(self, image, changeset):
        """
        Given an existing Image instance, create a new revision based on it.

        This new revision will be where the replacement is stored.
        """
        return RevisionManager._clone_revision(self,
                                               instance=image,
                                               instance_class=Image,
                                               changeset=changeset)

    def _do_create_revision(self, image, changeset, **ignore):
        """
        Helper delegate to do the class-specific work of clone_revision.
        """
        revision = ImageRevision(
            # revision-specific fields:
            image=image,
            changeset=changeset,

            # copied fields:
            content_type=image.content_type,
            object_id=image.object_id,
            type=image.type)

        revision.save()
        return revision


def _clear_image_cache(cached_image):
    cached_image.storage.delete(cached_image.path)
    cached_image.cachefile_backend.set_state(cached_image,
                                             CacheFileState.DOES_NOT_EXIST)


class ImageRevision(Revision):
    class Meta:
        db_table = 'oi_image_revision'
        ordering = ['created', '-id']

    objects = ImageRevisionManager()

    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True,
                              related_name='revisions')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=True)
    object_id = models.PositiveIntegerField(db_index=True, null=True)
    object = GenericForeignKey('content_type', 'object_id')

    type = models.ForeignKey(ImageType, on_delete=models.CASCADE)

    image_file = models.ImageField(upload_to='%s/%%m_%%Y' %
                                             settings.NEW_GENERIC_IMAGE_DIR)
    scaled_image = ImageSpecField([ResizeToFit(width=400)],
                                  source='image_file',
                                  format='JPEG', options={'quality': 90})
    cropped_face = ImageSpecField([CropToFace(), ],
                                  source='image_file',
                                  format='JPEG',
                                  options={'quality': 90})

    marked = models.BooleanField(default=False)
    is_replacement = models.BooleanField(default=False)

    def description(self):
        return '%s for %s' % (self.type.description,
                              str(self.object.full_name()))

    def _get_source(self):
        return self.image

    def _get_source_name(self):
        return 'image'

    def _get_blank_values(self):
        """
        Images don't do field comparisons, so just return an empty
        dictionary so we don't throw an exception if code calls this.
        """
        return {}

    def calculate_imps(self, prev_rev=None):
        return IMP_IMAGE_VALUE

    def _imps_for(self, field_name):
        """
        Images are done purely on a flat point model and don't really have
        fields.  We shouldn't get here, but just in case, return 0 to be safe.
        """
        return 0

    def commit_to_display(self):
        image = self.image
        if self.is_replacement:
            prev_rev = self.previous()
            # copy replaced image back to revision
            prev_rev.image_file.save(str(prev_rev.id) + '.jpg',
                                     content=image.image_file)
            image.image_file.delete()
        elif self.deleted:
            image.delete()
            return
        elif image is None:
            if self.type.unique and not self.is_replacement:
                if Image.objects.filter(
                        content_type=ContentType.objects
                                                .get_for_model(self.object),
                        object_id=self.object.id,
                        type=self.type,
                        deleted=False).count():
                    raise ErrorWithMessage(
                          '%s has an %s. Additional images cannot be uploaded,'
                          ' only replacements are possible.' %
                          (self.object, self.type.description))

            # first generate instance
            image = Image(content_type=self.content_type,
                          object_id=self.object_id,
                          type=self.type,
                          marked=self.marked)
            image.save()

        # then add the uploaded file
        image.image_file.save(str(image.id) + '.jpg', content=self.image_file)
        self.image_file.delete()
        self.image = image
        if self.is_replacement:
            _clear_image_cache(image.scaled_image)
            _clear_image_cache(image.thumbnail)
            _clear_image_cache(image.icon)
            _clear_image_cache(image.cropped_face)
        self.save()

    def __str__(self):
        return '%s for %s' % (self.type.description.capitalize(),
                              str(self.object))


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
        return DataSourceRevision.objects.filter(
          revision_id=self.revision.id,
          content_type=ContentType.objects.get_for_model(self.revision))


class DataSourceRevisionManager(RevisionManager):
    def clone_revision(self, data_source, changeset, sourced_revision):
        """
        Given an existing DataSource instance, create a new revision
        based on it.

        This new revision will be where the replacement is stored.
        """
        return RevisionManager._clone_revision(
                self,
                instance=data_source,
                instance_class=DataSource,
                changeset=changeset,
                sourced_revision=sourced_revision)

    def _do_create_revision(self, data_source, changeset,
                            sourced_revision, **ignore):
        """
        Helper delegate to do the class-specific work of c  lone_revision.
        """
        revision = DataSourceRevision(
                # revision-specific fields:
                data_source=data_source,
                changeset=changeset,
                # copied fields:
                sourced_revision=sourced_revision,
                source_description=data_source.source_description,
                source_type=data_source.source_type,
                field=data_source.field
        )

        revision.save()
        return revision


class DataSourceRevision(Revision):
    """
    Indicates the various sources of data
    """

    class Meta:
        db_table = 'oi_data_source_revision'
        ordering = ['created', '-id']
        verbose_name_plural = 'Data Source Revisions'

    objects = DataSourceRevisionManager()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=True)
    revision_id = models.IntegerField(db_index=True, null=True)
    sourced_revision = GenericForeignKey('content_type', 'revision_id')

    data_source = models.ForeignKey('gcd.DataSource',
                                    on_delete=models.CASCADE,
                                    related_name='revisions',
                                    null=True)
    source_type = models.ForeignKey('gcd.SourceType',
                                    on_delete=models.CASCADE)
    source_description = models.TextField()
    field = models.CharField(max_length=256)

    def _get_blank_values(self):
        return {
            'data_source': None,
            'source_type': None,
            'source_description': '',
            'field': '',
        }

    def _get_source(self):
        return self.data_source

    def _get_source_name(self):
        return 'data_source'

    def _field_list(self):
        field_list = ['source_description', 'source_type']
        return field_list

    def _imps_for(self, field_name):
        return 1

    def commit_to_display(self):
        # TODO add delete (and other stuff ?)
        data_source = self.data_source

        if data_source is None:
            data_source = DataSource(field=self.field)
        elif self.deleted:
            source_object = self.sourced_revision.source
            source_object.data_source.remove(data_source)
            data_source.delete()
            return
        data_source.source_type = self.source_type
        data_source.source_description = self.source_description
        data_source.save()

        if self.data_source is None:
            source_object = self.sourced_revision.source
            source_object.data_source.add(data_source)
            self.data_source = data_source
            self.save()

    def __str__(self):
        return '%s - %s' % (
            str(self.field), str(self.source_type.type))


def process_data_source(creator_form, field_name, changeset=None,
                        revision=None, sourced_revision=None):
    data_source = creator_form.cleaned_data.get('%s_source_type' % field_name)
    data_source_description = creator_form.cleaned_data.get(
                                          '%s_source_description' % field_name)

    if revision:
        # existing revision, data removed
        if not data_source and not data_source_description:
            if revision.source:
                revision.deleted = True
            else:
                revision.delete()
                return
        # existing revision, only update data
        else:
            revision.source_type = data_source
            revision.source_description = data_source_description
            revision.deleted = False
        revision.save()
    elif data_source or data_source_description:
        # new revision, create and set meta data
        revision = DataSourceRevision.objects.create(
                                source_type=data_source,
                                source_description=data_source_description,
                                changeset=changeset,
                                sourced_revision=sourced_revision,
                                field=field_name)


def reserve_data_sources(data_sources, changeset, sourced_revision,
                         delete=False):
    for data_source in data_sources:
        data_source_lock = _get_revision_lock(data_source,
                                              changeset=changeset)
        if data_source_lock is None:
            raise IntegrityError("needed DataSource lock not possible")
        data_source = DataSourceRevision.objects.clone_revision(
          data_source, changeset=changeset, sourced_revision=sourced_revision)
        if delete:
            data_source.deleted = True
            data_source.save()


def _get_creator_sourced_fields():
    return {'birth_place': 'birth_city_uncertain',
            'death_place': 'death_city_uncertain',
            'bio': 'bio'}


def get_creator_field_list():
    return ['disambiguation',
            'birth_date', 'birth_country', 'birth_country_uncertain',
            'birth_province', 'birth_province_uncertain',
            'birth_city', 'birth_city_uncertain',
            'death_date', 'death_country', 'death_country_uncertain',
            'death_province', 'death_province_uncertain',
            'death_city', 'death_city_uncertain',
            'whos_who', 'bio', 'notes'
            ]


class CreatorRevision(Revision):
    class Meta:
        db_table = 'oi_creator_revision'
        ordering = ['created', '-id']

    creator = models.ForeignKey('gcd.Creator',
                                on_delete=models.CASCADE,
                                null=True,
                                related_name='revisions')

    gcd_official_name = models.CharField(max_length=255, db_index=True)
    disambiguation = models.CharField(max_length=255, default='',
                                      db_index=True, blank=True)

    # TODO change from null=True
    birth_date = models.ForeignKey(Date, on_delete=models.CASCADE,
                                   related_name='+', null=True, blank=True)
    death_date = models.ForeignKey(Date, on_delete=models.CASCADE,
                                   related_name='+', null=True, blank=True)

    birth_country = models.ForeignKey('stddata.Country',
                                      on_delete=models.CASCADE,
                                      related_name='cr_birth_country',
                                      null=True, blank=True)
    birth_country_uncertain = models.BooleanField(default=False)
    birth_province = models.CharField(max_length=50, blank=True)
    birth_province_uncertain = models.BooleanField(default=False)
    birth_city = models.CharField(max_length=200, blank=True)
    birth_city_uncertain = models.BooleanField(default=False)

    death_country = models.ForeignKey('stddata.Country',
                                      on_delete=models.CASCADE,
                                      related_name='cr_death_country',
                                      null=True, blank=True)
    death_country_uncertain = models.BooleanField(default=False)
    death_province = models.CharField(max_length=50, blank=True)
    death_province_uncertain = models.BooleanField(default=False)
    death_city = models.CharField(max_length=200, blank=True)
    death_city_uncertain = models.BooleanField(default=False)

    whos_who = models.URLField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    external_link_revisions = GenericRelation(ExternalLinkRevision)

    notes = models.TextField(blank=True, default='')

    source_name = 'creator'
    source_class = Creator

    @property
    def source(self):
        return self.creator

    @source.setter
    def source(self, value):
        self.creator = value

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        # clone date instances
        birth_date = self.creator.birth_date
        birth_date.pk = None
        birth_date.save()
        self.birth_date = birth_date

        death_date = self.creator.death_date
        death_date.pk = None
        death_date.save()
        self.death_date = death_date

    def _do_create_dependent_revisions(self, delete=False):
        name_details = self.creator.active_names()
        for name_detail in name_details:
            name_lock = _get_revision_lock(name_detail,
                                           changeset=self.changeset)
            if name_lock is None:
                raise IntegrityError("needed Name lock not possible")
            creator_name = CreatorNameDetailRevision.clone(name_detail,
                                                           self.changeset)
            creator_name.save_added_revision(changeset=self.changeset,
                                             creator_revision=self)

            if delete:
                creator_name.deleted = True
                creator_name.save()

        data_sources = self.creator.data_source.all()
        reserve_data_sources(data_sources, self.changeset, self, delete)

        if delete:
            for creator_art_influence in self.creator.active_art_influences():
                influence_lock = _get_revision_lock(creator_art_influence,
                                                    changeset=self.changeset)
                if influence_lock is None:
                    raise IntegrityError("needed CreatorArtInfluence lock not"
                                         " possible")
                creator_art_influence_revision = \
                    CreatorArtInfluenceRevision.clone(creator_art_influence,
                                                      self.changeset)
                creator_art_influence_revision.deleted = True
                creator_art_influence_revision.save()

            for received_award in self.creator.active_awards():
                award_lock = _get_revision_lock(received_award,
                                                changeset=self.changeset)
                if award_lock is None:
                    raise IntegrityError("needed ReceivedAward lock not "
                                         "possible")
                received_award_revision = \
                    ReceivedAwardRevision.clone(received_award,
                                                self.changeset)
                received_award_revision.deleted = True
                received_award_revision.save()

            for creator_degree in self.creator.active_degrees():
                degree_lock = _get_revision_lock(creator_degree,
                                                 changeset=self.changeset)
                if degree_lock is None:
                    raise IntegrityError("needed CreatorDegree lock not "
                                         "possible")
                creator_degree_revision = \
                    CreatorDegreeRevision.clone(creator_degree,
                                                self.changeset)
                creator_degree_revision.deleted = True
                creator_degree_revision.save()

            for creator_membership in self.creator.active_memberships():
                membership_lock = _get_revision_lock(creator_membership,
                                                     changeset=self.changeset)
                if membership_lock is None:
                    raise IntegrityError("needed CreatorMembership lock not "
                                         "possible")
                creator_membership_revision = \
                    CreatorMembershipRevision.clone(creator_membership,
                                                    self.changeset)
                creator_membership_revision.deleted = True
                creator_membership_revision.save()

            for creator_non_comic_work in \
                    self.creator.active_non_comic_works():
                noncomicwork_lock = _get_revision_lock(
                  creator_non_comic_work, changeset=self.changeset)
                if noncomicwork_lock is None:
                    raise IntegrityError("needed CreatorNonComicWork lock not"
                                         " possible")
                creator_non_comic_work_revision = \
                    CreatorNonComicWorkRevision.clone(creator_non_comic_work,
                                                      self.changeset)
                creator_non_comic_work_revision.deleted = True
                creator_non_comic_work_revision.save()

            for creator_school in self.creator.active_schools():
                school_lock = _get_revision_lock(creator_school,
                                                 changeset=self.changeset)
                if school_lock is None:
                    raise IntegrityError("needed CreatorSchool lock not "
                                         "possible")
                creator_school_revision = \
                    CreatorSchoolRevision.clone(creator_school,
                                                self.changeset)
                creator_school_revision.deleted = True
                creator_school_revision.save()

    def extra_forms(self, request):
        from apps.oi.forms.creator import CreatorRevisionFormSet
        from apps.oi.forms.support import CREATOR_HELP_LINKS
        from apps.oi.forms import get_date_revision_form

        creator_names_formset = CreatorRevisionFormSet(
          request.POST or None, instance=self,
          queryset=self.cr_creator_names.filter(deleted=False))
        form_class = get_date_revision_form(self,
                                            user=request.user,
                                            date_help_links=CREATOR_HELP_LINKS)
        birth_date_form = form_class(request.POST or None,
                                     prefix='birth_date',
                                     instance=self.birth_date)
        death_date_form = form_class(request.POST or None,
                                     prefix='death_date',
                                     instance=self.death_date)
        birth_date_form.fields['date'].label = 'Birth date'
        death_date_form.fields['date'].label = 'Death date'

        external_link_formset = self._create_external_link_formset(request)

        return {'creator_names_formset': creator_names_formset,
                'birth_date_form': birth_date_form,
                'death_date_form': death_date_form,
                'external_link_formset': external_link_formset
                }

    def process_extra_forms(self, extra_forms):
        creator_names_formset = extra_forms['creator_names_formset']
        # TODO use _process_formset, but needs to handle official name update
        removed_names = creator_names_formset.deleted_forms
        for creator_name_form in creator_names_formset:
            if creator_name_form.is_valid() and creator_name_form.cleaned_data\
               and creator_name_form not in removed_names:
                cd = creator_name_form.cleaned_data
                if 'id' in cd and cd['id']:
                    creator_revision = creator_name_form.save()
                else:
                    creator_revision = creator_name_form.save(commit=False)
                    creator_revision.save_added_revision(
                      changeset=self.changeset, creator_revision=self)
                if cd['is_official_name']:
                    self.gcd_official_name = cd['name']
            elif (
              not creator_name_form.is_valid() and
              creator_name_form not in creator_names_formset.deleted_forms
            ):
                raise ValueError

        if removed_names:
            _removed_related_objects(removed_names, 'creator_name_detail')

        birth_date_form = extra_forms['birth_date_form']
        death_date_form = extra_forms['death_date_form']
        self.birth_date = birth_date_form.save()
        self.death_date = death_date_form.save()
        self.save()
        # TODO support more than one revision
        data_source_revision = self.changeset\
            .datasourcerevisions.filter(field='birth_date')
        if data_source_revision:
            data_source_revision = data_source_revision[0]
        process_data_source(birth_date_form, 'birth_date', self.changeset,
                            revision=data_source_revision,
                            sourced_revision=self)
        data_source_revision = self.changeset\
            .datasourcerevisions.filter(field='death_date')
        if data_source_revision:
            data_source_revision = data_source_revision[0]
        process_data_source(death_date_form, 'death_date', self.changeset,
                            revision=data_source_revision,
                            sourced_revision=self)

        self._process_external_link_formset(extra_forms)

    def _pre_save_object(self, changes):
        name = self.changeset.creatornamedetailrevisions.get(
                                                         is_official_name=True)
        self.creator.sort_name = name.sort_name

        if self.added:
            # clone date instances
            birth_date = self.birth_date
            birth_date.pk = None
            birth_date.save()
            self.creator.birth_date = birth_date

            death_date = self.death_date
            death_date.pk = None
            death_date.save()
            self.creator.death_date = death_date
        else:
            ctr = self.creator
            ctr.birth_date.set(year=self.birth_date.year,
                               month=self.birth_date.month,
                               day=self.birth_date.day,
                               year_uncertain=self.birth_date.year_uncertain,
                               month_uncertain=self.birth_date.month_uncertain,
                               day_uncertain=self.birth_date.day_uncertain,
                               empty=True)
            ctr.birth_date.save()
            ctr.death_date.set(year=self.death_date.year,
                               month=self.death_date.month,
                               day=self.death_date.day,
                               year_uncertain=self.death_date.year_uncertain,
                               month_uncertain=self.death_date.month_uncertain,
                               day_uncertain=self.death_date.day_uncertain,
                               empty=True)
            ctr.death_date.save()

    def _handle_dependents(self, changes):
        # for new creator, we need to save the record_id in the name revisions
        if self.added:
            for name in self.changeset.creatornamedetailrevisions.all():
                name.creator = self.creator
                name.save()

    def get_absolute_url(self):
        if self.creator is None:
            return "/creator/revision/%i/preview" % self.id
        return self.creator.get_absolute_url()

    def __str__(self):
        return '%s' % str(self.gcd_official_name)

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    def _field_list(self):
        return get_creator_field_list()

    def _get_blank_values(self):
        return {
            'gcd_official_name': '',
            'cr_creator_names': '',
            'disambiguation': '',
            'birth_date': '',
            'death_date': '',
            'whos_who': '',
            'birth_country': None,
            'birth_country_uncertain': False,
            'birth_province': '',
            'birth_province_uncertain': False,
            'birth_city': '',
            'birth_city_uncertain': False,
            'death_country': None,
            'death_country_uncertain': False,
            'death_province': '',
            'death_province_uncertain': False,
            'death_city': '',
            'death_city_uncertain': False,
            'bio': '',
            'notes': '',
        }

    def _start_imp_sum(self):
        self._seen_birth_country = False
        self._seen_birth_province = False
        self._seen_birth_city = False
        self._seen_death_country = False
        self._seen_death_province = False
        self._seen_death_city = False

    def _imps_for(self, field_name):
        if field_name in ('birth_country',
                          'birth_country_uncertain'):
            if not self._seen_birth_country:
                self._seen_birth_country = True
                return 1
        elif field_name in ('birth_province',
                            'birth_province_uncertain'):
            if not self._seen_birth_province:
                self._seen_birth_province = True
                return 1
        elif field_name in ('birth_city',
                            'birth_city_uncertain'):
            if not self._seen_birth_city:
                self._seen_birth_city = True
                return 1
        elif field_name in ('death_country',
                            'death_country_uncertain'):
            if not self._seen_death_country:
                self._seen_death_country = True
                return 1
        elif field_name in ('death_province',
                            'death_province_uncertain'):
            if not self._seen_death_province:
                self._seen_death_province = True
                return 1
        elif field_name in ('death_city',
                            'death_city_uncertain'):
            if not self._seen_death_city:
                self._seen_death_city = True
                return 1
        elif field_name in self._field_list():
            return 1
        return 0


class PreviewCreator(Creator):
    class Meta:
        proxy = True

    def active_names(self):
        return self.revision.changeset.creatornamedetailrevisions\
                                      .filter(deleted=False)

    @property
    def data_source(self):
        return DataSourceRevision.objects.filter(
          revision_id=self.revision.id,
          content_type=ContentType.objects.get_for_model(self.revision))


class CreatorRelationRevision(Revision):
    """
    Relations between creators to relate any GCD Official name to any other
    name.
    """

    class Meta:
        db_table = 'oi_creator_relation_revision'
        ordering = ('to_creator', 'relation_type', 'from_creator')
        verbose_name_plural = 'Creator Relation Revisions'

    creator_relation = models.ForeignKey('gcd.CreatorRelation',
                                         on_delete=models.CASCADE,
                                         null=True,
                                         related_name='revisions')

    to_creator = models.ForeignKey('gcd.Creator', on_delete=models.CASCADE,
                                   related_name='to_creator_revisions')
    relation_type = models.ForeignKey('gcd.RelationType',
                                      on_delete=models.CASCADE,
                                      related_name='revisions')
    from_creator = models.ForeignKey('gcd.Creator', on_delete=models.CASCADE,
                                     related_name='from_creator_revisions')
    creator_name = models.ManyToManyField(
                          'gcd.CreatorNameDetail', blank=True,
                          related_name='creator_relation_revisions')
    notes = models.TextField(blank=True)

    source_name = 'creator_relation'
    source_class = CreatorRelation

    @property
    def source(self):
        return self.creator_relation

    @source.setter
    def source(self, value):
        self.creator_relation = value

    _base_field_list = ['from_creator', 'relation_type', 'to_creator',
                        'creator_name', 'notes']

    def _field_list(self):
        field_list = self._base_field_list
        return field_list

    def _get_blank_values(self):
        return {
            'from_creator': None,
            'to_creator': None,
            'relation_type': None,
            'creator_name': None,
            'notes': ''
        }

    def _get_source(self):
        return self.creator_relation

    def _get_source_name(self):
        return 'creator_relation'

    def _imps_for(self, field_name):
        return 1

    def _do_create_dependent_revisions(self, delete=False):
        data_sources = self.creator_relation.data_source.all()
        reserve_data_sources(data_sources, self.changeset, self, delete)

    def commit_to_display(self):
        creator_relation = self.creator_relation

        if creator_relation is None:
            creator_relation = CreatorRelation()
        elif self.deleted:
            creator_relation.delete()
            return

        creator_relation.to_creator = self.to_creator
        creator_relation.from_creator = self.from_creator
        creator_relation.relation_type = self.relation_type
        creator_relation.notes = self.notes
        creator_relation.save()
        creator_relation.creator_name.clear()
        if self.creator_name.count():
            creator_relation.creator_name.add(*list(self.creator_name.all().
                                                    values_list('id',
                                                                flat=True)))

        if self.creator_relation is None:
            self.creator_relation = creator_relation
            self.save()

    def __str__(self):
        return '%s >%s< %s' % (str(self.from_creator),
                               str(self.relation_type),
                               str(self.to_creator)
                               )


class CreatorNameDetailRevision(Revision):
    """
    record of the creator's name
    """

    class Meta:
        db_table = 'oi_creator_name_detail_revision'
        ordering = ['sort_name', '-creator__birth_date__year', 'type__id']
        verbose_name_plural = 'Creator Name Detail Revisions'

    creator_name_detail = models.ForeignKey('gcd.CreatorNameDetail',
                                            on_delete=models.CASCADE,
                                            null=True,
                                            related_name='revisions')
    creator_revision = models.ForeignKey(CreatorRevision,
                                         on_delete=models.CASCADE,
                                         related_name='cr_creator_names',
                                         null=True)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE,
                                related_name='name_revisions', null=True)
    name = models.CharField(max_length=255, db_index=True)
    sort_name = models.CharField(max_length=255, default='')
    is_official_name = models.BooleanField(default=False)
    given_name = models.CharField(max_length=255, db_index=True, default='',
                                  blank=True)
    family_name = models.CharField(max_length=255, db_index=True, default='',
                                   blank=True)
    type = models.ForeignKey('gcd.NameType', on_delete=models.CASCADE,
                             related_name='revision_name_details',
                             null=True, blank=True)
    in_script = models.ForeignKey(Script, on_delete=models.CASCADE,
                                  default=Script.LATIN_PK)

    source_name = 'creator_name_detail'
    source_class = CreatorNameDetail

    @property
    def source(self):
        return self.creator_name_detail

    @source.setter
    def source(self, value):
        self.creator_name_detail = value

    def _do_complete_added_revision(self, creator_revision):
        self.creator_revision = creator_revision

    def _post_create_for_add(self, changes):
        self.creator = self.creator_revision.creator

    def __str__(self):
        if self.creator.disambiguation:
            extra = ' [%s]' % self.creator.disambiguation
        else:
            extra = ''
        if self.is_official_name:
            return '%s%s' % (str(self.creator), extra)
        else:
            return '%s%s - %s' % (str(self.creator), extra, str(self.name))

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    def _field_list(self):
        field_list = ['name', 'sort_name', 'is_official_name', 'given_name',
                      'family_name', 'type', 'in_script']
        return field_list

    def _get_blank_values(self):
        return {
            'name': '',
            'sort_name': '',
            'given_name': '',
            'family_name': '',
            'is_official_name': False,
            'type': None,
            'in_script': ''
        }

    def _imps_for(self, field_name):
        if field_name == 'sort_name':
            if self.sort_name == self.name:
                return 0
            else:
                return 1
        if field_name in self._field_list():
            return 1
        return 0


class CreatorSignatureRevision(Revision):
    """
    record of a creator's signature
    """

    class Meta:
        db_table = 'oi_creator_signature_revision'
        ordering = ['name', '-creator__sort_name',
                    '-creator__birth_date__year']
        verbose_name_plural = 'Creator Signature Revisions'

    creator_signature = models.ForeignKey('gcd.CreatorSignature',
                                          on_delete=models.CASCADE,
                                          null=True,
                                          related_name='revisions')
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE,
                                related_name='signature_revisions')
    name = models.CharField(max_length=255)
    generic = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    image_revision = models.ForeignKey(ImageRevision,
                                       on_delete=models.CASCADE,
                                       null=True,
                                       related_name='signature_revisions')

    source_name = 'creator_signature'
    source_class = CreatorSignature

    @property
    def source(self):
        return self.creator_signature

    @source.setter
    def source(self, value):
        self.creator_signature = value

    def _do_complete_added_revision(self, creator):
        self.creator = creator

    def _do_create_dependent_revisions(self, delete=False):
        data_sources = self.creator_signature.data_source.all()
        reserve_data_sources(data_sources, self.changeset, self, delete)

    def _handle_dependents(self, changes):
        self._handle_dependent_image_revision()

    def full_name(self):
        return str(self)

    def __str__(self):
        return '%s signature %s' % (str(self.creator),
                                    self.name)

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['name', 'generic', 'notes']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'name': '',
            'generic': False,
            'notes': ''
        }

    def _imps_for(self, field_name):
        if field_name in self._field_list():
            return 1
        return 0


class CreatorSchoolRevision(Revision):
    """
    record the schools creators attended
    """

    class Meta:
        db_table = 'oi_creator_school_revision'
        ordering = ['created', '-id']
        verbose_name_plural = 'Creator School Revisions'

    creator_school = models.ForeignKey('gcd.CreatorSchool',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       related_name='revisions')
    creator = models.ForeignKey('gcd.Creator', on_delete=models.CASCADE,
                                related_name='school_revisions')
    school = models.ForeignKey('gcd.School', on_delete=models.CASCADE,
                               related_name='cr_schools')
    school_year_began = models.PositiveSmallIntegerField(null=True, blank=True)
    school_year_began_uncertain = models.BooleanField(default=False)
    school_year_ended = models.PositiveSmallIntegerField(null=True, blank=True)
    school_year_ended_uncertain = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    source_name = 'creator_school'
    source_class = CreatorSchool

    @property
    def source(self):
        return self.creator_school

    @source.setter
    def source(self, value):
        self.creator_school = value

    def _do_complete_added_revision(self, creator):
        self.creator = creator

    def _do_create_dependent_revisions(self, delete=False):
        data_sources = self.creator_school.data_source.all()
        reserve_data_sources(data_sources, self.changeset, self, delete)

    def get_absolute_url(self):
        if self.creator_school is None:
            return "/creator_school/revision/%i/preview" % self.id
        return self.creator_school.get_absolute_url()

    def __str__(self):
        return '%s - %s' % (
            str(self.creator), str(self.school.school_name))

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['school',
                        'school_year_began', 'school_year_began_uncertain',
                        'school_year_ended', 'school_year_ended_uncertain',
                        'notes']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'school': None,
            'school_year_began': None,
            'school_year_began_uncertain': False,
            'school_year_ended': None,
            'school_year_ended_uncertain': False,
            'notes': ''
        }

    def _start_imp_sum(self):
        self._seen_year_began = False
        self._seen_year_ended = False

    def _imps_for(self, field_name):
        if field_name in ('school_year_began',
                          'school_year_began_uncertain'):
            if not self._seen_year_began:
                self._seen_year_began = True
                return 1
        elif field_name in ('school_year_ended',
                            'school_year_ended_uncertain'):
            if not self._seen_year_ended:
                self._seen_year_ended = True
                return 1
        elif field_name in self._base_field_list:
            return 1
        return 0


class PreviewCreatorSchool(CreatorSchool):
    class Meta:
        proxy = True

    @property
    def data_source(self):
        return DataSourceRevision.objects.filter(
          revision_id=self.revision.id,
          content_type=ContentType.objects.get_for_model(self.revision))


class CreatorDegreeRevision(Revision):
    """
    record the degrees creators received
    """

    class Meta:
        db_table = 'oi_creator_degree_revision'
        ordering = ['created', '-id']
        verbose_name_plural = 'Creator Degree Revisions'

    creator_degree = models.ForeignKey('gcd.CreatorDegree',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       related_name='revisions')
    creator = models.ForeignKey('gcd.Creator', on_delete=models.CASCADE,
                                related_name='degree_revisions')
    school = models.ForeignKey('gcd.School', on_delete=models.CASCADE,
                               related_name='creator_degrees',
                               null=True)
    degree = models.ForeignKey('gcd.Degree', on_delete=models.CASCADE,
                               related_name='creator_degrees')
    degree_year = models.PositiveSmallIntegerField(null=True, blank=True)
    degree_year_uncertain = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    source_name = 'creator_degree'
    source_class = CreatorDegree

    @property
    def source(self):
        return self.creator_degree

    @source.setter
    def source(self, value):
        self.creator_degree = value

    def _do_complete_added_revision(self, creator):
        self.creator = creator

    def _do_create_dependent_revisions(self, delete=False):
        data_sources = self.creator_degree.data_source.all()
        reserve_data_sources(data_sources, self.changeset, self, delete)

    def get_absolute_url(self):
        if self.creator_degree is None:
            return "/creator_degree/revision/%i/preview" % self.id
        return self.creator_degree.get_absolute_url()

    def __str__(self):
        return '%s - %s' % (
            str(self.creator), str(self.degree.degree_name))

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['school', 'degree',
                        'degree_year', 'degree_year_uncertain', 'notes']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'school': None,
            'degree': None,
            'degree_year': None,
            'degree_year_uncertain': False,
            'notes': ''
        }

    def _start_imp_sum(self):
        self._seen_year = False

    def _imps_for(self, field_name):
        if field_name in ('degree_year',
                          'degree_year_uncertain'):
            if not self._seen_year:
                self._seen_year = True
                return 1
        elif field_name in self._base_field_list:
            return 1
        return 0


class PreviewCreatorDegree(CreatorDegree):
    class Meta:
        proxy = True

    @property
    def data_source(self):
        return DataSourceRevision.objects.filter(
          revision_id=self.revision.id,
          content_type=ContentType.objects.get_for_model(self.revision))


class CreatorMembershipRevision(Revision):
    """
    record the membership of creator
    """

    class Meta:
        db_table = 'oi_creator_membership_revision'
        ordering = ['created', '-id']
        verbose_name_plural = 'Creator Membership Revisions'

    creator_membership = models.ForeignKey('gcd.CreatorMembership',
                                           on_delete=models.CASCADE,
                                           null=True,
                                           related_name='revisions')
    creator = models.ForeignKey('gcd.Creator', on_delete=models.CASCADE,
                                related_name='membership_revisions')
    organization_name = models.CharField(max_length=200)
    membership_type = models.ForeignKey('gcd.MembershipType',
                                        on_delete=models.CASCADE,
                                        related_name='cr_membershiptype',
                                        null=True,
                                        blank=True)
    membership_year_began = models.PositiveSmallIntegerField(null=True,
                                                             blank=True)
    membership_year_began_uncertain = models.BooleanField(default=False)
    membership_year_ended = models.PositiveSmallIntegerField(null=True,
                                                             blank=True)
    membership_year_ended_uncertain = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    source_name = 'creator_membership'
    source_class = CreatorMembership

    @property
    def source(self):
        return self.creator_membership

    @source.setter
    def source(self, value):
        self.creator_membership = value

    def _do_complete_added_revision(self, creator):
        self.creator = creator

    def _do_create_dependent_revisions(self, delete=False):
        data_sources = self.creator_membership.data_source.all()
        reserve_data_sources(data_sources, self.changeset, self, delete)

    def get_absolute_url(self):
        if self.creator_membership is None:
            return "/creator_membership/revision/%i/preview" % self.id
        return self.creator_membership.get_absolute_url()

    def __str__(self):
        return '%s: %s' % (self.creator, str(self.organization_name))

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['organization_name',
                        'membership_type',
                        'membership_year_began',
                        'membership_year_began_uncertain',
                        'membership_year_ended',
                        'membership_year_ended_uncertain',
                        'notes',
                        ]

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'organization_name': '',
            'membership_type': None,
            'membership_year_began': None,
            'membership_year_began_uncertain': False,
            'membership_year_ended': None,
            'membership_year_ended_uncertain': False,
            'notes': '',
        }

    def _start_imp_sum(self):
        self._seen_year_began = False
        self._seen_year_ended = False

    def _imps_for(self, field_name):
        if field_name in ('membership_year_began',
                          'membership_year_began_uncertain'):
            if not self._seen_year_began:
                self._seen_year_began = True
                return 1
        elif field_name in ('membership_year_ended',
                            'membership_year_ended_uncertain'):
            if not self._seen_year_ended:
                self._seen_year_ended = True
                return 1
        elif field_name in self._base_field_list:
            return 1
        return 0


class PreviewCreatorMembership(CreatorMembership):
    class Meta:
        proxy = True

    @property
    def data_source(self):
        return DataSourceRevision.objects.filter(
          revision_id=self.revision.id,
          content_type=ContentType.objects.get_for_model(self.revision))


class CreatorArtInfluenceRevision(Revision):
    """
    record the art influences of creator
    """

    class Meta:
        db_table = 'oi_creator_art_influence_revision'
        ordering = ['created', '-id']
        verbose_name_plural = 'Creator Art Influence Revisions'

    creator_art_influence = models.ForeignKey('gcd.CreatorArtInfluence',
                                              on_delete=models.CASCADE,
                                              null=True,
                                              related_name='revisions')
    creator = models.ForeignKey('gcd.Creator', on_delete=models.CASCADE,
                                related_name='art_influence_revisions')
    influence_name = models.CharField(max_length=200, blank=True)
    influence_link = models.ForeignKey('gcd.Creator',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       blank=True,
                                       related_name='influenced_revisions')
    notes = models.TextField(blank=True)

    source_name = 'creator_art_influence'
    source_class = CreatorArtInfluence

    @property
    def source(self):
        return self.creator_art_influence

    @source.setter
    def source(self, value):
        self.creator_art_influence = value

    def _do_complete_added_revision(self, creator):
        self.creator = creator

    def _do_create_dependent_revisions(self, delete=False):
        data_sources = self.creator_art_influence.data_source.all()
        reserve_data_sources(data_sources, self.changeset, self, delete)

    def get_absolute_url(self):
        if self.creator_art_influence is None:
            return "/creator_art_influence/revision/%i/preview" % self.id
        return self.creator_art_influence.get_absolute_url()

    def __str__(self):
        if self.influence_name:
            influence = self.influence_name
        else:
            influence = self.influence_link

        return '%s: %s' % (self.creator, influence)

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['influence_name',
                        'influence_link',
                        'notes',
                        ]

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'influence_name': '',
            'influence_link': None,
            'notes': '',
        }

    def _imps_for(self, field_name):
        if field_name in self._base_field_list:
            return 1
        return 0


class PreviewCreatorArtInfluence(CreatorArtInfluence):
    class Meta:
        proxy = True

    @property
    def data_source(self):
        return DataSourceRevision.objects.filter(
          revision_id=self.revision.id,
          content_type=ContentType.objects.get_for_model(self.revision))


class MultiURLValidator(URLValidator):
    def __call__(self, value):
        for url in value.split('\n'):
            try:
                super(URLValidator, self).__call__(url.strip())
            except ValidationError as e:
                if e.message != 'Enter a valid URL.':
                    raise
                else:
                    raise ValidationError('Enter one or more valid URLs, '
                                          'one per line.')


class CreatorNonComicWorkRevision(Revision):
    """
    record the non comic work of creator
    """

    class Meta:
        db_table = 'oi_creator_non_comic_work_revision'
        ordering = ['created', '-id']
        verbose_name_plural = 'Creator NonComicWork Revisions'

    creator_non_comic_work = models.ForeignKey('gcd.CreatorNonComicWork',
                                               on_delete=models.CASCADE,
                                               null=True,
                                               related_name='revisions')
    creator = models.ForeignKey('gcd.Creator', on_delete=models.CASCADE,
                                related_name='non_comic_work_revisions')
    work_type = models.ForeignKey('gcd.NonComicWorkType',
                                  on_delete=models.CASCADE,
                                  related_name='cr_worktype')
    publication_title = models.CharField(max_length=200)
    employer_name = models.CharField(max_length=200, blank=True)
    work_title = models.CharField(max_length=255, blank=True)
    work_role = models.ForeignKey('gcd.NonComicWorkRole',
                                  on_delete=models.CASCADE,
                                  null=True,
                                  blank=True,
                                  related_name='cr_workrole')
    work_years = models.TextField(blank=True)
    work_urls = models.TextField(blank=True, validators=[MultiURLValidator()])
    notes = models.TextField(blank=True)

    source_name = 'creator_non_comic_work'
    source_class = CreatorNonComicWork

    @property
    def source(self):
        return self.creator_non_comic_work

    @source.setter
    def source(self, value):
        self.creator_non_comic_work = value

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        self.work_years = self.creator_non_comic_work.display_years()

    def _do_complete_added_revision(self, creator):
        self.creator = creator

    def _do_create_dependent_revisions(self, delete=False):
        data_sources = self.creator_non_comic_work.data_source.all()
        reserve_data_sources(data_sources, self.changeset, self, delete)

    def _save_work_years(self, ncw, year, year_uncertain):
        ncw_year, created = NonComicWorkYear.objects\
          .get_or_create(non_comic_work=ncw, work_year=year)
        ncw_year.work_year_uncertain = year_uncertain
        ncw_year.save()
        if not created:
            self.existing_years.remove(ncw_year.id)

    def _post_save_object(self, changes):
        if self.work_years:
            ncw = self.creator_non_comic_work
            self.existing_years = list(NonComicWorkYear.objects
                                       .filter(non_comic_work=ncw)
                                       .values_list('id', flat=True))
            for year in self.work_years.split(';'):
                range_split = year.split('-')
                if len(range_split) == 2:
                    year_began = _check_year(range_split[0])
                    year_end = _check_year(range_split[1])
                    if year_began > year_end:
                        raise ValueError

                    self._save_work_years(ncw, year_began,
                                          '?' in range_split[0])
                    self._save_work_years(ncw, year_end,
                                          '?' in range_split[1])

                    if '?' in range_split[1] and '?' in range_split[0]:
                        years_uncertain = True
                    else:
                        years_uncertain = False
                    for i in range(year_began + 1, year_end):
                        self._save_work_years(ncw, i, years_uncertain)
                else:
                    year_number = _check_year(year)
                    self._save_work_years(ncw, year_number, '?' in year)

            # remove years which are not present in value anymore
            for i in self.existing_years:
                ncw_year = NonComicWorkYear.objects.get(id=i)
                ncw_year.delete()

    def get_absolute_url(self):
        if self.creator_non_comic_work is None:
            return "/creator_non_comic_work/revision/%i/preview" % self.id
        return self.creator_non_comic_work.get_absolute_url()

    def __str__(self):
        return '%s: %s' % (str(self.creator),
                           str(self.publication_title))

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    _base_field_list = ['work_type',
                        'publication_title',
                        'employer_name',
                        'work_title',
                        'work_role',
                        'work_years',
                        'work_urls',
                        'notes',
                        ]

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'work_type': '',
            'publication_title': '',
            'employer_name': '',
            'work_title': '',
            'work_role': '',
            'work_years': '',
            'work_urls': '',
            'notes': '',
        }

    def _imps_for(self, field_name):
        if field_name in self._base_field_list:
            return 1
        return 0


class PreviewCreatorNonComicWork(CreatorNonComicWork):
    class Meta:
        proxy = True

    def display_years(self):
        return self.revision.work_years

    @property
    def data_source(self):
        return DataSourceRevision.objects.filter(
          revision_id=self.revision.id,
          content_type=ContentType.objects.get_for_model(self.revision))


# #########################################################################
# Revision-definition validation (roadmap B0). Field identity in the revision
# system is name strings matched to model attributes at runtime, so a rename
# silently turns a lookup into a no-op -- the brand_emblem class of bug. The
# validators now live in a submodule (first step of the C1 split); re-export
# them so `from apps.oi.models import validate_*` keeps working.
from apps.oi.models.validation import (  # noqa: E402
    validate_revision_definitions,
    validate_revision_field_lists,
    _concrete_revision_classes,
    _walk_field_path,
    _revision_attr_exists,
)
