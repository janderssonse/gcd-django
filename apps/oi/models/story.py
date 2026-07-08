"""Story revision cluster (roadmap C1): story, story-credit, story-character, character-order, story-group, story-arc revisions, StoryRevision/PreviewStory and BiblioEntryRevision. Base classes and helpers come from apps.oi.models.base; re-exported through the package __init__ so the historical import surface is unchanged."""

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
        from apps.oi.models import CreatorSignatureRevision
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
        from apps.oi.models import ReprintRevision
        revs = ReprintRevision.objects \
                              .exclude(changeset__id=self.changeset_id)\
                              .exclude(changeset__state=states.DISCARDED)
        return revs

    def from_reprints_oi(self, preview=False):
        from apps.oi.models import ReprintRevision
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
        from apps.oi.models import ReprintRevision
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


