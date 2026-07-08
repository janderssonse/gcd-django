"""Publisher / brand / printer revision cluster (roadmap C1). Extracted from the models package; base classes and helpers come from apps.oi.models.base, re-exported through the package __init__ so the historical import surface is unchanged."""

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


class PublisherRevisionBase(Revision):
    class Meta:
        abstract = True

    name = models.CharField(max_length=255)

    year_began = models.IntegerField(null=True, blank=True)
    year_ended = models.IntegerField(null=True, blank=True)
    year_began_uncertain = models.BooleanField(default=False)
    year_ended_uncertain = models.BooleanField(default=False)
    year_overall_began = models.IntegerField(null=True, blank=True)
    year_overall_ended = models.IntegerField(null=True, blank=True)
    year_overall_began_uncertain = models.BooleanField(default=False)
    year_overall_ended_uncertain = models.BooleanField(default=False)

    notes = models.TextField(blank=True)
    keywords = models.TextField(blank=True, default='')
    url = models.URLField(blank=True)

    def __str__(self):
        if self.source is None:
            return self.name
        return str(self.source)

    ######################################
    # TODO old methods, t.b.c

    # order exactly as desired in compare page
    # use list instead of set to control order
    _base_field_list = ['name',
                        'year_began',
                        'year_began_uncertain',
                        'year_ended',
                        'year_ended_uncertain',
                        'year_overall_began',
                        'year_overall_began_uncertain',
                        'year_overall_ended',
                        'year_overall_ended_uncertain',
                        'url',
                        'notes',
                        'keywords']

    def _field_list(self):
        return self._base_field_list

    def _get_blank_values(self):
        return {
            'name': '',
            'year_began': None,
            'year_ended': None,
            'year_began_uncertain': None,
            'year_ended_uncertain': None,
            'year_overall_began': None,
            'year_overall_ended': None,
            'year_overall_began_uncertain': None,
            'year_overall_ended_uncertain': None,
            'url': '',
            'notes': '',
            'keywords': '',
        }

    def _start_imp_sum(self):
        self._seen_year_began = False
        self._seen_year_ended = False

    def _imps_for(self, field_name):
        years_found, value = _imps_for_years(self, field_name,
                                             'year_began', 'year_ended')
        if years_found:
            return value
        overall_years_found, value = _imps_for_years(self, field_name,
                                                     'year_overall_began',
                                                     'year_overall_ended')
        if overall_years_found:
            return value
        elif field_name in self._base_field_list:
            return 1
        return 0


class PublisherRevision(PublisherRevisionBase):
    class Meta:
        db_table = 'oi_publisher_revision'
        ordering = ['-created', '-id']

    publisher = models.ForeignKey('gcd.Publisher', on_delete=models.CASCADE,
                                  null=True, related_name='revisions')

    country = models.ForeignKey('stddata.Country', on_delete=models.CASCADE,
                                db_index=True)

    # Deprecated fields about relating publishers/imprints to each other
    # TODO can these be removed, or does it make problems for the
    # change history of publishers ? Should not need to worry
    # about change history of old imprints
    is_master = models.BooleanField(default=True, db_index=True)
    parent = models.ForeignKey('gcd.Publisher', on_delete=models.CASCADE,
                               default=None, null=True, blank=True,
                               db_index=True, related_name='imprint_revisions')
    external_link_revisions = GenericRelation(ExternalLinkRevision)

    date_inferred = models.BooleanField(default=False)

    source_name = 'publisher'
    source_class = Publisher

    @property
    def source(self):
        return self.publisher

    @source.setter
    def source(self, value):
        self.publisher = value

    _update_stats = True

    def _do_create_dependent_revisions(self, delete=False):
        if delete:
            for indicia_publisher in self.publisher\
                                         .active_indicia_publishers():
                # indicia_publisher is deletable if publisher is deletable
                indicia_publishers_lock = _get_revision_lock(
                                          indicia_publisher,
                                          changeset=self.changeset)
                if indicia_publishers_lock is None:
                    raise IntegrityError("needed IndiciaPublisher lock not"
                                         " possible")
                indicia_publisher_revision = IndiciaPublisherRevision.clone(
                                                indicia_publisher,
                                                self.changeset)
                indicia_publisher_revision.deleted = True
                indicia_publisher_revision.save()
            for brand_use in self.publisher.branduse_set.all():
                brand_use_lock = _get_revision_lock(brand_use,
                                                    changeset=self.changeset)
                if brand_use_lock is None:
                    raise IntegrityError("needed BrandUse lock not possible")
                brand_use_revision = BrandUseRevision.clone(brand_use,
                                                            self.changeset)
                brand_use_revision.deleted = True
                brand_use_revision.save()

    def extra_forms(self, request):
        external_link_formset = self._create_external_link_formset(request)
        return {'external_link_formset': external_link_formset}

    def process_extra_forms(self, extra_forms):
        self._process_external_link_formset(extra_forms)

    def get_absolute_url(self):
        if self.publisher is None:
            return "/publisher/revision/%i/preview" % self.id
        return self.publisher.get_absolute_url()

    ######################################
    # TODO old methods, t.b.c

    def _queue_name(self):
        return '%s (%s, %s)' % (self.name, self.year_began,
                                self.country.code.upper())

    def _field_list(self):
        fields = []
        fields.extend(PublisherRevisionBase._field_list(self))
        fields.insert(fields.index('url'), 'country')
        fields.extend(('is_master', 'parent'))
        return fields

    def _get_blank_values(self):
        blank_values = PublisherRevisionBase._get_blank_values(self)
        blank_values['country'] = None
        blank_values['is_master'] = True
        blank_values['parent'] = None
        return blank_values

    def _imps_for(self, field_name):
        # We don't actually ever change parent and is_master since imprint
        # objects are hidden from direct access by the indexer.
        if field_name == 'country':
            return 1
        return PublisherRevisionBase._imps_for(self, field_name)

    def has_keywords(self):
        return self.keywords

    def display_keywords(self):
        return self.keywords


class IndiciaPublisherRevision(PublisherRevisionBase):
    class Meta:
        db_table = 'oi_indicia_publisher_revision'
        ordering = ['-created', '-id']

    indicia_publisher = models.ForeignKey('gcd.IndiciaPublisher',
                                          on_delete=models.CASCADE, null=True,
                                          related_name='revisions')

    is_surrogate = models.BooleanField(default=False)

    country = models.ForeignKey('stddata.Country', on_delete=models.CASCADE,
                                db_index=True,
                                related_name='indicia_publishers_revisions')

    parent = models.ForeignKey('gcd.Publisher', on_delete=models.CASCADE,
                               null=True, blank=True, db_index=True,
                               related_name='indicia_publisher_revisions')

    source_name = 'indicia_publisher'
    source_class = IndiciaPublisher

    @property
    def source(self):
        return self.indicia_publisher

    @source.setter
    def source(self, value):
        self.indicia_publisher = value

    @classmethod
    def _get_parent_field_tuples(cls):
        return frozenset({('parent',)})

    def _do_complete_added_revision(self, parent):
        self.parent = parent

    def get_absolute_url(self):
        if self.indicia_publisher is None:
            return "/indicia_publisher/revision/%i/preview" % self.id
        return self.indicia_publisher.get_absolute_url()

    ######################################
    # TODO old methods, t.b.c

    def _field_list(self):
        fields = []
        fields.extend(PublisherRevisionBase._field_list(self))
        fields.insert(fields.index('url'), 'is_surrogate')
        fields.insert(fields.index('url'), 'country')
        fields.append('parent')
        return fields

    def _get_blank_values(self):
        blank_values = PublisherRevisionBase._get_blank_values(self)
        blank_values['country'] = None
        blank_values['is_surrogate'] = True
        blank_values['parent'] = None
        return blank_values

    def _imps_for(self, field_name):
        if field_name in ['is_surrogate', 'parent', 'country']:
            return 1
        return PublisherRevisionBase._imps_for(self, field_name)

    def _queue_name(self):
        return '%s: %s (%s, %s)' % (self.parent.name,
                                    self.name,
                                    self.year_began,
                                    self.country.code.upper())


class BrandGroupRevision(PublisherRevisionBase):
    class Meta:
        db_table = 'oi_brand_group_revision'
        ordering = ['-created', '-id']

    brand_group = models.ForeignKey('gcd.BrandGroup', on_delete=models.CASCADE,
                                    null=True, related_name='revisions')

    parent = models.ForeignKey('gcd.Publisher', on_delete=models.CASCADE,
                               null=True, blank=True, db_index=True,
                               related_name='brand_group_revisions')

    source_name = 'brand_group'
    source_class = BrandGroup

    @property
    def source(self):
        return self.brand_group

    @source.setter
    def source(self, value):
        self.brand_group = value

    @classmethod
    def _get_parent_field_tuples(cls):
        return frozenset({('parent',)})

    def _handle_dependents(self, changes):
        if self.added:
            brand_revision = BrandRevision(
                changeset=self.changeset,
                name=self.name,
                year_began=self.year_began,
                year_ended=self.year_ended,
                year_began_uncertain=self.year_began_uncertain,
                year_ended_uncertain=self.year_ended_uncertain)
            brand_revision.save()
            brand_revision.group.add(self.brand_group)
            brand_revision.commit_to_display()

    def _do_complete_added_revision(self, parent):
        self.parent = parent

    def get_absolute_url(self):
        if self.brand_group is None:
            return "/brand_group/revision/%i/preview" % self.id
        return self.brand_group.get_absolute_url()

    ######################################
    # TODO old methods, t.b.c

    def _field_list(self):
        fields = []
        fields.extend(PublisherRevisionBase._field_list(self))
        fields.append('parent')
        return fields

    def _get_blank_values(self):
        blank_values = PublisherRevisionBase._get_blank_values(self)
        blank_values['parent'] = None
        return blank_values

    def _imps_for(self, field_name):
        if field_name == 'parent':
            return 1
        return PublisherRevisionBase._imps_for(self, field_name)

    def _queue_name(self):
        return '%s: %s (%s)' % (self.parent.name, self.name, self.year_began)


class BrandRevision(PublisherRevisionBase):
    class Meta:
        db_table = 'oi_brand_revision'
        ordering = ['-created', '-id']

    brand = models.ForeignKey('gcd.Brand', on_delete=models.CASCADE,
                              null=True, related_name='revisions')
    # parent needs to be kept for old revisions
    parent = models.ForeignKey('gcd.Publisher', on_delete=models.CASCADE,
                               null=True, blank=True, db_index=True,
                               related_name='brand_revisions')
    group = models.ManyToManyField('gcd.BrandGroup', blank=False,
                                   related_name='brand_revisions')
    generic = models.BooleanField(default=False)

    image_revision = models.ForeignKey('oi.ImageRevision',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       related_name='brand_emblem_revisions')

    source_name = 'brand'
    source_class = Brand

    @property
    def source(self):
        return self.brand

    @source.setter
    def source(self, value):
        self.brand = value

    @classmethod
    def _get_parent_field_tuples(cls):
        return frozenset({('group',)})

    def _do_create_dependent_revisions(self, delete=False):
        if delete:
            for brand_use in self.brand.in_use.all():
                # TODO check if transaction rollback works
                brand_use_lock = _get_revision_lock(
                                brand_use,
                                changeset=self.changeset)
                if brand_use_lock is None:
                    raise IntegrityError("needed BrandUse lock not possible")

                use_revision = BrandUseRevision.clone(brand_use,
                                                      self.changeset)
                use_revision.deleted = True
                use_revision.save()

    def _handle_dependents(self, changes):
        if self.added:
            parent_ids = set(self.brand.group.values_list('parent_id',
                                                          flat=True))
            for parent_id in parent_ids:
                use = BrandUseRevision(
                    changeset=self.changeset,
                    emblem=self.brand,
                    publisher_id=parent_id,
                    year_began=self.year_began,
                    year_began_uncertain=self.year_began_uncertain,
                    year_ended=self.year_ended,
                    year_ended_uncertain=self.year_ended_uncertain)
                use.save()
                use.commit_to_display()
        self._handle_dependent_image_revision()

    def get_absolute_url(self):
        if self.brand is None:
            return "/brand/revision/%i/preview" % self.id
        return self.brand.get_absolute_url()

    ######################################
    # TODO old methods, t.b.c

    def _field_list(self):
        fields = []
        fields.extend(PublisherRevisionBase._field_list(self))
        fields.append('parent')
        fields.insert(fields.index('url'), 'group')
        fields.insert(fields.index('year_began'), 'generic')
        return fields

    def _get_blank_values(self):
        blank_values = PublisherRevisionBase._get_blank_values(self)
        blank_values['parent'] = None
        blank_values['group'] = True
        blank_values['generic'] = False
        return blank_values

    def _imps_for(self, field_name):
        if field_name in ['group', 'generic']:
            return 1
        return PublisherRevisionBase._imps_for(self, field_name)

    def _queue_name(self):
        return '%s: %s (%s)' % (self.group.all()[0].name, self.name,
                                self.year_began)

    def full_name(self):
        return self.__str__()


class PreviewBrand(Brand):
    class Meta:
        proxy = True

    @property
    def TODOgroup(self):
        return self._group.all()


def get_brand_use_field_list():
    return ['year_began', 'year_began_uncertain',
            'year_ended', 'year_ended_uncertain', 'notes']


class BrandUseRevision(Revision):
    class Meta:
        db_table = 'oi_brand_use_revision'
        ordering = ['-created', '-id']

    brand_use = models.ForeignKey('gcd.BrandUse', on_delete=models.CASCADE,
                                  null=True, related_name='revisions')

    emblem = models.ForeignKey('gcd.Brand', on_delete=models.CASCADE,
                               null=True, related_name='use_revisions')

    publisher = models.ForeignKey('gcd.Publisher', on_delete=models.CASCADE,
                                  null=True, db_index=True,
                                  related_name='brand_use_revisions')

    year_began = models.IntegerField(db_index=True, null=True)
    year_ended = models.IntegerField(null=True)
    year_began_uncertain = models.BooleanField(default=False)
    year_ended_uncertain = models.BooleanField(default=False)
    notes = models.TextField(max_length=255, blank=True)

    source_name = 'brand_use'
    source_class = BrandUse

    @property
    def source(self):
        return self.brand_use

    @source.setter
    def source(self, value):
        self.brand_use = value

    def _pre_delete(self, changes):
        for revision in self.source.revisions.all():
            setattr(revision, 'brand_use_id', None)
            revision.save()
        self.brand_use_id = None

    def _do_complete_added_revision(self, emblem, publisher):
        """
        Do the necessary processing to complete the fields of a new
        BrandUse revision for adding a record before it can be saved.
        """
        self.publisher = publisher
        self.emblem = emblem

    def __str__(self):
        return 'brand emblem %s used by %s.' % (self.emblem, self.publisher)

    ######################################
    # TODO old methods, t.b.c

    def _field_list(self):
        fields = get_brand_use_field_list()
        return fields

    def _get_blank_values(self):
        return {
            'publisher': None,
            'year_began': None,
            'year_ended': None,
            'year_began_uncertain': None,
            'year_ended_uncertain': None,
            'notes': ''
        }

    def _start_imp_sum(self):
        self._seen_year_began = False
        self._seen_year_ended = False

    def _imps_for(self, field_name):
        if field_name in ('year_began', 'year_began_uncertain'):
            if not self._seen_year_began:
                self._seen_year_began = True
                return 1
        elif field_name in ('year_ended', 'year_ended_uncertain'):
            if not self._seen_year_ended:
                self._seen_year_ended = True
                return 1
        else:
            return 1
        return 0

    def _queue_name(self):
        return '%s at %s (%s)' % (self.emblem.name, self.publisher.name,
                                  self.year_began)


class PrinterRevision(PublisherRevisionBase):
    class Meta:
        db_table = 'oi_printer_revision'
        ordering = ['-created', '-id']

    printer = models.ForeignKey('gcd.Printer', on_delete=models.CASCADE,
                                null=True, related_name='revisions')

    country = models.ForeignKey('stddata.Country', on_delete=models.CASCADE,
                                db_index=True)

    source_name = 'printer'
    source_class = Printer

    @property
    def source(self):
        return self.printer

    @source.setter
    def source(self, value):
        self.printer = value

    _update_stats = True

    def _do_create_dependent_revisions(self, delete=False):
        if delete:
            for indicia_printer in self.printer\
                                       .active_indicia_printers():
                # indicia_printer is deletable if printer is deletable
                indicia_printers_lock = _get_revision_lock(
                                        indicia_printer,
                                        changeset=self.changeset)
                if indicia_printers_lock is None:
                    raise IntegrityError("needed IndiciaPrinter lock not"
                                         " possible")
                indicia_printer_revision = IndiciaPrinterRevision.clone(
                                             indicia_printer,
                                             self.changeset)
                indicia_printer_revision.deleted = True
                indicia_printer_revision.save()

    def get_absolute_url(self):
        if self.printer is None:
            return "/printer/revision/%i/preview" % self.id
        return self.printer.get_absolute_url()

    ######################################
    # TODO old methods, t.b.c

    def _queue_name(self):
        return '%s (%s, %s)' % (self.name, self.year_began,
                                self.country.code.upper())

    def _field_list(self):
        fields = []
        fields.extend(PublisherRevisionBase._field_list(self))
        fields.insert(fields.index('url'), 'country')
        return fields

    def _get_blank_values(self):
        blank_values = PublisherRevisionBase._get_blank_values(self)
        blank_values['country'] = None
        return blank_values

    def _imps_for(self, field_name):
        if field_name == 'country':
            return 1
        return PublisherRevisionBase._imps_for(self, field_name)


class IndiciaPrinterRevision(PublisherRevisionBase):
    class Meta:
        db_table = 'oi_indicia_printer_revision'
        ordering = ['-created', '-id']

    indicia_printer = models.ForeignKey('gcd.IndiciaPrinter',
                                        on_delete=models.CASCADE, null=True,
                                        related_name='revisions')

    country = models.ForeignKey('stddata.Country', on_delete=models.CASCADE,
                                db_index=True,
                                related_name='indicia_printers_revisions')

    parent = models.ForeignKey('gcd.Printer', on_delete=models.CASCADE,
                               null=True, blank=True, db_index=True,
                               related_name='indicia_printer_revisions')

    source_name = 'indicia_printer'
    source_class = IndiciaPrinter

    @property
    def source(self):
        return self.indicia_printer

    @source.setter
    def source(self, value):
        self.indicia_printer = value

    @classmethod
    def _get_parent_field_tuples(cls):
        return frozenset({('parent',)})

    def _do_complete_added_revision(self, parent):
        self.parent = parent

    def get_absolute_url(self):
        if self.indicia_printer is None:
            return "/indicia_printer/revision/%i/preview" % self.id
        return self.indicia_printer.get_absolute_url()

    ######################################
    # TODO old methods, t.b.c

    def _field_list(self):
        fields = []
        fields.extend(PublisherRevisionBase._field_list(self))
        fields.insert(fields.index('url'), 'country')
        fields.append('parent')
        return fields

    def _get_blank_values(self):
        blank_values = PublisherRevisionBase._get_blank_values(self)
        blank_values['country'] = None
        blank_values['parent'] = None
        return blank_values

    def _imps_for(self, field_name):
        if field_name in ['parent', 'country']:
            return 1
        return PublisherRevisionBase._imps_for(self, field_name)

    def _queue_name(self):
        return '%s: %s (%s, %s)' % (self.parent.name,
                                    self.name,
                                    self.year_began,
                                    self.country.code.upper())


