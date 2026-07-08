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

# series cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.series import (  # noqa: F401
    get_series_field_list, SeriesRevision, SeriesBondRevisionManager,
    get_series_bond_field_list, SeriesBondRevision)

# issue cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.issue import (  # noqa: F401
    get_issue_field_list, PublisherCodeNumberRevision, IssueCreditRevision,
    IssueRevision, PreviewIssue)

# story cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.story import (  # noqa: F401
    get_story_field_list, StoryCreditRevision, StoryCharacterRevision,
    CharacterOrderRevision, CharacterThroughOrderRevision, StoryGroupRevision,
    StoryArcRevision, StoryArcRelationRevision, _order_civilian_after_alias,
    StoryRevision, PreviewStory, BiblioEntryRevision)

# feature cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.feature import (  # noqa: F401
    FeatureRevision, FeatureLogoRevision, FeatureRelationRevision)

LANGUAGE_STATS = ['de']

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


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
