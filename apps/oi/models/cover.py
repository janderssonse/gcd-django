"""Cover revision cluster (roadmap C1). Base classes and helpers come from apps.oi.models.base; re-exported through the package __init__ so the historical import surface is unchanged."""

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
    RevisionQuerySet, Revision, OngoingReservation)

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


class CoverRevisionManager(RevisionManager):
    """
    Custom manager allowing the cloning of revisions from existing rows.
    """

    def clone_revision(self, cover, changeset):
        """
        Given an existing Cover instance, create a new revision based on it.

        This new revision will be where the replacement is stored.
        """
        return RevisionManager._clone_revision(self,
                                               instance=cover,
                                               instance_class=Cover,
                                               changeset=changeset)

    def _do_create_revision(self, cover, changeset, **ignore):
        """
        Helper delegate to do the class-specific work of clone_revision.
        """
        revision = CoverRevision(
            # revision-specific fields:
            cover=cover,
            changeset=changeset,

            # copied fields:
            issue=cover.issue)

        revision.save()
        return revision


class CoverRevision(Revision):
    class Meta:
        db_table = 'oi_cover_revision'
        ordering = ['-created', '-id']

    objects = CoverRevisionManager()

    cover = models.ForeignKey(Cover, on_delete=models.CASCADE,
                              null=True, related_name='revisions')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE,
                              related_name='cover_revisions')

    marked = models.BooleanField(default=False)
    is_replacement = models.BooleanField(default=False)
    is_wraparound = models.BooleanField(default=False)
    front_left = models.IntegerField(default=0, null=True)
    front_right = models.IntegerField(default=0, null=True)
    front_bottom = models.IntegerField(default=0, null=True)
    front_top = models.IntegerField(default=0, null=True)

    file_source = models.CharField(max_length=255, null=True)

    def _get_source(self):
        return self.cover

    def _get_source_name(self):
        return 'cover'

    def _get_blank_values(self):
        """
        Covers don't do field comparisons, so just return an empty
        dictionary so we don't throw an exception if code calls this.
        """
        return {}

    def calculate_imps(self, prev_rev=None):
        if self.changeset.change_type != CTYPES['cover']:
            return 1
        return IMP_COVER_VALUE

    def _imps_for(self, field_name):
        """
        Covers are done purely on a flat point model and don't really have
        fields.  We shouldn't get here, but just in case, return 0 to be safe.
        """
        return 0

    def commit_to_display(self):
        # the file handling is in the view/covers code
        cover = self.cover

        if cover is None:
            # check for variants having added issue records
            issue_revisions = self.changeset.issuerevisions.all()
            if len(issue_revisions) == 0:
                cover = Cover(issue=self.issue)
            elif len(issue_revisions) == 1:
                if not issue_revisions[0].issue:
                    issue_revisions[0].commit_to_display()
                cover = Cover(issue=issue_revisions[0].issue)
                self.issue = cover.issue
            else:
                raise NotImplementedError
            cover.save()
        elif self.deleted:
            cover.delete()
            cover.save()
            update_count('covers', -1,
                         language=cover.issue.series.language,
                         country=cover.issue.series.country)
            if cover.issue.series.scan_count == 0:
                series = cover.issue.series
                series.has_gallery = False
                series.save()
            return

        if self.cover and self.is_replacement is False:
            # this is a move of a cover
            if self.changeset.change_type in [CTYPES['variant_add'],
                                              CTYPES['two_issues']]:
                old_issue = cover.issue
                issue_rev = self.changeset.issuerevisions\
                                          .exclude(issue=old_issue).get()
                cover.issue = issue_rev.issue
                cover.save()
                if issue_rev.series != old_issue.series:
                    if (issue_rev.series.language !=
                        old_issue.series.language) \
                       or (issue_rev.series.country !=
                           old_issue.series.country):
                        update_count('covers', -1,
                                     language=old_issue.series.language,
                                     country=old_issue.series.country)
                        update_count('covers', 1,
                                     language=issue_rev.series.language,
                                     country=issue_rev.series.country)
                    if not issue_rev.series.has_gallery:
                        issue_rev.series.has_gallery = True
                        issue_rev.series.save()
                    if old_issue.series.scan_count == 0:
                        old_issue.series.has_gallery = False
                        old_issue.series.save()
            else:
                # implement in case we do different kind if cover moves
                raise NotImplementedError
        else:
            from apps.oi.covers import copy_approved_cover
            if self.cover is None:
                self.cover = cover
                self.save()
                update_count('covers', 1,
                             language=cover.issue.series.language,
                             country=cover.issue.series.country)
                if not cover.issue.series.has_gallery:
                    series = cover.issue.series
                    series.has_gallery = True
                    series.save()
            copy_approved_cover(self)
            cover.marked = self.marked
            cover.last_upload = self.changeset.comments \
                                    .latest('created').created
            cover.is_wraparound = self.is_wraparound
            cover.front_left = self.front_left
            cover.front_right = self.front_right
            cover.front_top = self.front_top
            cover.front_bottom = self.front_bottom
            cover.save()

    def base_dir(self):
        return (settings.MEDIA_ROOT + settings.NEW_COVERS_DIR +
                self.changeset.created.strftime('%B_%Y/').lower())

    def approved_file(self):
        if not settings.BETA:
            if (self.created > settings.NEW_SITE_COVER_CREATION_DATE and
                not (self.deleted and
                     (self.previous().created <
                      settings.NEW_SITE_COVER_CREATION_DATE))):
                if self.changeset.state == states.APPROVED or self.deleted:
                    if self.deleted:
                        suffix = "/uploads/%d_%s" % (
                            self.cover.id,
                            self.previous().changeset
                                           .created.strftime('%Y%m%d_%H%M%S'))
                    else:
                        suffix = "/uploads/%d_%s" % (
                            self.cover.id,
                            self.changeset.created.strftime('%Y%m%d_%H%M%S'))
                    return "%s%s%d%s%s" % (
                        settings.IMAGE_SERVER_URL,
                        settings.COVERS_DIR,
                        int(self.cover.id / 1000),
                        suffix,
                        os.path.splitext(glob.glob(self.cover.base_dir() +
                                                   suffix + '*')[0])[1])
                else:
                    filename = "%s/%d" % (self.base_dir(), self.id)
                    return "%s%s%s%d%s" % (
                        settings.IMAGE_SERVER_URL,
                        settings.NEW_COVERS_DIR,
                        self.changeset.created.strftime('%B_%Y/').lower(),
                        self.id,
                        os.path.splitext(glob.glob(filename + '*')[0])[1])
            else:
                return "not supported for covers from the old site"
        else:
            return "not supported on BETA"

    def get_absolute_url(self):
        if self.cover is None:
            return "/cover/revision/%i/preview" % self.id
        return self.cover.get_absolute_url()

    def __str__(self):
        return str(self.issue)


