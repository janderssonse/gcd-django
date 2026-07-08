"""Issue revision cluster (roadmap C1): issue, issue-credit and publisher-code-number revisions plus PreviewIssue. Base classes and helpers come from apps.oi.models.base; re-exported through the package __init__ so the historical import surface is unchanged."""

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
from apps.oi.models.cover import CoverRevision

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


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
            from apps.oi.models import StoryRevision
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
            from apps.oi.models import (
                StoryRevision, StoryCreditRevision, CharacterOrderRevision,
                StoryCharacterRevision, StoryGroupRevision)
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
        from apps.oi.models import ReprintRevision
        revs = ReprintRevision.objects \
                              .exclude(changeset__id=self.changeset_id)\
                              .exclude(changeset__state=states.DISCARDED)
        return revs

    def from_reprints_oi(self, preview=False):
        from apps.oi.models import ReprintRevision
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
        from apps.oi.models import ReprintRevision
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
        from apps.oi.models import ReprintRevision
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
        from apps.oi.models import ReprintRevision
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
        from apps.oi.models import PreviewStory
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


