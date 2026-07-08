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

# character cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.character import (  # noqa: F401
    UniverseRevision, PreviewUniverse, CharacterGroupRevisionBase,
    CharacterRevision, PreviewCharacter, CharacterNameDetailRevision,
    CharacterRelationRevision, GroupRevision, GroupNameDetailRevision,
    GroupRelationRevision, GroupMembershipRevision)

# reprint cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.reprint import (  # noqa: F401
    get_reprint_field_list, ReprintRevision)

# image cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.image import (  # noqa: F401
    ImageRevisionManager, _clear_image_cache, ImageRevision)

# award cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.award import (  # noqa: F401
    AwardRevision, ReceivedAwardRevision, PreviewReceivedAward)

# datasource cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.datasource import (  # noqa: F401
    DataSourceRevisionManager, DataSourceRevision, process_data_source,
    reserve_data_sources)

LANGUAGE_STATS = ['de']

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


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
