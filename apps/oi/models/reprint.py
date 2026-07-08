"""Reprint revision cluster (roadmap C1). Base classes and helpers come from apps.oi.models.base; re-exported through the package __init__ so the historical import surface is unchanged."""

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
from apps.oi.models.story import StoryRevision

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


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


