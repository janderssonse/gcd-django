"""Data-source revision cluster (roadmap C1): DataSourceRevision plus the process_data_source/reserve_data_sources helpers. Base classes and helpers come from apps.oi.models.base; re-exported through the package __init__ so the historical import surface is unchanged."""

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


