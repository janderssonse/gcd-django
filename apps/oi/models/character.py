"""Character, group and universe revision cluster (roadmap C1): universe, character (+ name-detail/relation), group (+ name-detail/relation/membership) revisions and the shared CharacterGroupRevisionBase, plus PreviewCharacter/PreviewUniverse. Base classes and helpers come from apps.oi.models.base; re-exported through the package __init__ so the historical import surface is unchanged."""

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


