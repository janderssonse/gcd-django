"""
Revision-system base layer (roadmap C1).

Holds the changeset/revision machinery that every concrete entity revision
builds on: the ChangeType/CTYPES vocabulary, imp-scoring and keyword helpers,
the Changeset/ChangesetComment models, the revision-lock primitives, the
Revision base class with its managers, and OngoingReservation.

Concrete entity revisions (StoryRevision, IssueRevision, ...) live in the
package __init__ and subclass Revision from here. The base class only needs
those subclasses inside method bodies, so those references are lazy imports
(from apps.oi.models import ...) to avoid an import-time cycle.
"""

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

LANGUAGE_STATS = ['de']

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


__all__ = [
    'ChangeType', 'CTYPES', 'CTYPES_INLINE', 'CTYPES_BULK',
    'ACTION_ADD', 'ACTION_DELETE', 'ACTION_MODIFY',
    'IMP_BONUS_ADD', 'IMP_COVER_VALUE', 'IMP_IMAGE_VALUE',
    'IMP_APPROVER_VALUE', 'IMP_DELETE',
    'update_count', 'set_series_first_last', 'validated_isbn',
    'remove_leading_article', 'on_sale_date_as_string', 'on_sale_date_fields',
    'get_keywords', 'save_keywords', '_check_year', '_imps_for_years',
    '_get_revision_lock', '_free_revision_lock',
    '_removed_related_objects', '_process_formset',
    'Changeset', 'ChangesetComment', 'RevisionLock', 'RevisionManager',
    'RevisionQuerySet', 'Revision', 'OngoingReservation',
]

# Changeset type. ChangeType is the canonical definition; CTYPES is kept
# as a backwards-compatible name -> value map for the many existing call
# sites (CTYPES['issue'] etc.).
class ChangeType(models.IntegerChoices):
    UNKNOWN = 0
    PUBLISHER = 1
    BRAND = 2
    INDICIA_PUBLISHER = 3
    SERIES = 4
    ISSUE_ADD = 5
    ISSUE = 6
    COVER = 7
    ISSUE_BULK = 8
    VARIANT_ADD = 9
    TWO_ISSUES = 10
    REPRINT = 11
    IMAGE = 12
    BRAND_GROUP = 13
    BRAND_USE = 14
    SERIES_BOND = 15
    CREATOR = 16
    CREATOR_ART_INFLUENCE = 17
    RECEIVED_AWARD = 18
    CREATOR_DEGREE = 19
    CREATOR_MEMBERSHIP = 20
    CREATOR_NON_COMIC_WORK = 21
    CREATOR_RELATION = 22
    CREATOR_SCHOOL = 23
    AWARD = 24
    FEATURE = 25
    FEATURE_LOGO = 26
    FEATURE_RELATION = 27
    PRINTER = 28
    INDICIA_PRINTER = 29
    CREATOR_SIGNATURE = 30
    CHARACTER = 31
    GROUP = 32
    GROUP_MEMBERSHIP = 33
    CHARACTER_RELATION = 34
    GROUP_RELATION = 35
    UNIVERSE = 36
    STORY_ARC = 37
    STORY_ARC_RELATION = 38


CTYPES = {change_type.name.lower(): change_type.value
          for change_type in ChangeType}

CTYPES_INLINE = frozenset((CTYPES['publisher'],
                           CTYPES['brand'],
                           CTYPES['brand_group'],
                           CTYPES['brand_use'],
                           CTYPES['indicia_publisher'],
                           CTYPES['printer'],
                           CTYPES['indicia_printer'],
                           CTYPES['series'],
                           CTYPES['story_arc'],
                           CTYPES['story_arc_relation'],
                           CTYPES['feature'],
                           CTYPES['feature_logo'],
                           CTYPES['feature_relation'],
                           CTYPES['universe'],
                           CTYPES['character'],
                           CTYPES['character_relation'],
                           CTYPES['group'],
                           CTYPES['group_relation'],
                           CTYPES['group_membership'],
                           CTYPES['cover'],
                           CTYPES['reprint'],
                           CTYPES['image'],
                           CTYPES['series_bond'],
                           CTYPES['award'],
                           CTYPES['creator'],
                           CTYPES['creator_art_influence'],
                           CTYPES['received_award'],
                           CTYPES['creator_degree'],
                           CTYPES['creator_membership'],
                           CTYPES['creator_non_comic_work'],
                           CTYPES['creator_relation'],
                           CTYPES['creator_school'],
                           CTYPES['creator_signature'],
                           ))

# Change types that *might* be bulk changes.  But might just have one revision.
CTYPES_BULK = frozenset((CTYPES['issue_bulk'],
                         CTYPES['issue_add']))

ACTION_ADD = 'bg-green-400'
ACTION_DELETE = 'bg-red-400'
ACTION_MODIFY = 'bg-yellow-400'

IMP_BONUS_ADD = 10
IMP_COVER_VALUE = 5
IMP_IMAGE_VALUE = 5
IMP_APPROVER_VALUE = 3
IMP_DELETE = 1


def update_count(field, delta, language=None, country=None):
    '''
    updates statistics, for all, per language, and per country
    CountStats with language=None is for all languages

    Thin wrapper around CountStats.objects.update_count for the cover-commit
    call sites; the manager method does the atomic single-query update.
    '''
    CountStats.objects.update_count(field, delta, language=language,
                                    country=country)


def set_series_first_last(series):
    '''
    set first_issue and last_issue for given series
    '''
    issues = series.active_issues().order_by('sort_code')
    if issues.count() == 0:
        series.first_issue = None
        series.last_issue = None
    else:
        series.first_issue = issues[0]
        series.last_issue = issues[len(issues) - 1]
    series.save()


def validated_isbn(entered_isbn):
    '''
    returns ISBN10 or ISBN13 if valid ISBN, empty string otherwiese
    '''
    isbns = entered_isbn.split(';')
    valid_isbns = True
    for num in isbns:
        valid_isbns &= isbn.is_valid(num)
    if valid_isbns and len(isbns) == 1:
        return isbn.compact(isbns[0])
    elif valid_isbns and len(isbns) == 2:
        compacted_isbns = [isbn.compact(isbn.to_isbn13(i)) for i in isbns]
        # if two ISBNs it must be corresponding ISBN10 and ISBN13
        if compacted_isbns[0] == compacted_isbns[1]:
            # always store ISBN13 if both exist
            return compacted_isbns[0]
    return ''


def remove_leading_article(name):
    '''
    returns the name with the leading article (separated by "'"
    or whitespace) removed
    '''
    article_match = re.match(r"\S?\w+['\s]\s*(.*)$", name, re.UNICODE)
    if article_match:
        return article_match.group(1)
    else:
        return name


def on_sale_date_as_string(issue):
    date = ''
    if issue.year_on_sale:
        date += f'{issue.year_on_sale:?<4d}'
    elif issue.day_on_sale or issue.month_on_sale:
        date += '????'
    if issue.month_on_sale:
        date += f'-{issue.month_on_sale:02d}'
    elif issue.day_on_sale:
        date += '-??'
    if issue.day_on_sale:
        date += f'-{issue.day_on_sale:02d}'
    return date


def on_sale_date_fields(on_sale_date):
    year_string = on_sale_date[:4].strip('?')
    if year_string:
        year = int(year_string)
    else:
        year = None
    month = None
    day = None
    if len(on_sale_date) > 4:
        month_string = on_sale_date[5:7].strip('?')
        if month_string:
            month = int(month_string)
        if len(on_sale_date) > 7:
            day = int(on_sale_date[8:10].strip('?'))
    return year, month, day


def get_keywords(source):
    return '; '.join(str(i) for i in source.keywords.all()
                                           .order_by('name'))


def save_keywords(revision, source):
    if revision.keywords:
        source.keywords.set([x.strip() for x in revision.keywords.split(';')])
        revision.keywords = '; '.join(
            str(i) for i in source.keywords.all().order_by('name'))
        revision.save()
    else:
        source.keywords.set([])


def _check_year(year):
    year = year.strip().strip('?')
    year_number = int(year)
    if len(year) != 4 or year_number < 0:
        raise forms.ValidationError('Enter valid years.')
    return year_number


def _imps_for_years(revision, field_name, year_began, year_ended):
    if field_name in (year_began, year_began + '_uncertain'):
        if not revision._seen_year_began and revision.__dict__[year_began]:
            revision._seen_year_began = True
            return True, 1
        return True, 0
    elif field_name in (year_ended, year_ended + '_uncertain'):
        if not revision._seen_year_ended and revision.__dict__[year_ended]:
            revision._seen_year_ended = True
            return True, 1
        return True, 0
    return False, None


class Changeset(models.Model):

    state = models.IntegerField(db_index=True,
                                choices=states.ChangesetState.choices)

    indexer = models.ForeignKey('auth.User', on_delete=models.CASCADE,
                                db_index=True,
                                related_name='changesets')
    along_with = models.ManyToManyField(User,
                                        related_name='changesets_assisting')
    on_behalf_of = models.ManyToManyField(User,
                                          related_name='changesets_source')

    # Changesets don't get an approver until late in the workflow,
    # and for legacy cases we don't know who they were.
    approver = models.ForeignKey('auth.User', on_delete=models.CASCADE,
                                 db_index=True,
                                 related_name='approved_%(class)s', null=True)

    # In production, change_type is a tinyint(2) due to the small value set.
    change_type = models.IntegerField(db_index=True,
                                      choices=ChangeType.choices)
    migrated = models.BooleanField(default=False, db_index=True)
    date_inferred = models.BooleanField(default=False)

    imps = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        self._inline_revision = None

    def _revision_sets(self):
        if self.change_type in [CTYPES['issue'], CTYPES['variant_add'],
                                CTYPES['two_issues']]:
            return (self.issuerevisions.all(),
                    self.issuecreditrevisions.all(),
                    self.storyrevisions.all(),
                    self.storycreditrevisions.all(),
                    self.storycharacterrevisions.all(),
                    self.storygrouprevisions.all(),
                    self.coverrevisions.all(),
                    self.reprintrevisions.all(),
                    self.publishercodenumberrevisions.all(),
                    self.externallinkrevisions.all(),
                    self.characterorderrevisions.all(),)

        if self.change_type in [CTYPES['issue_add'], CTYPES['issue_bulk']]:
            if self.issuerevisions.all().count() == 1 and \
               self.issuerevisions.get().variant_of:
                return (self.issuerevisions.all(),
                        self.issuecreditrevisions.all(),
                        self.storyrevisions.all(),
                        self.storycreditrevisions.all(),
                        self.storycharacterrevisions.all(),
                        self.storygrouprevisions.all(),
                        self.coverrevisions.all(),
                        self.reprintrevisions.all(),
                        self.publishercodenumberrevisions.all(),
                        self.externallinkrevisions.all(),
                        self.characterorderrevisions.all(),)
            elif self.issuerevisions.all().count() == 1:
                return (self.issuerevisions.all(),
                        self.issuecreditrevisions.all(),
                        self.publishercodenumberrevisions.all())
            else:
                return (self.issuerevisions.all().select_related('issue',
                                                                 'series'),
                        self.issuecreditrevisions.all(),)

        if self.change_type == CTYPES['cover']:
            return (self.coverrevisions.all(),
                    self.issuerevisions.all(),
                    self.storyrevisions.all())

        if self.change_type == CTYPES['story_arc']:
            return (self.storyarcrevisions.all(),)

        if self.change_type == CTYPES['story_arc_relation']:
            return (self.storyarcrelationrevisions.all(),)

        if self.change_type == CTYPES['feature']:
            return (self.featurerevisions.all(),
                    self.externallinkrevisions.all(),)

        if self.change_type == CTYPES['feature_logo']:
            return (self.featurelogorevisions.all(),
                    self.imagerevisions.all(),)

        if self.change_type == CTYPES['feature_relation']:
            return (self.featurerelationrevisions.all(),)

        if self.change_type == CTYPES['universe']:
            return (self.universerevisions.all(),)

        if self.change_type == CTYPES['character']:
            return (self.characterrevisions.all(),
                    self.characternamedetailrevisions.all(),
                    self.characterrelationrevisions.all(),
                    self.groupmembershiprevisions.all(),
                    self.externallinkrevisions.all())

        if self.change_type == CTYPES['character_relation']:
            return (self.characterrelationrevisions.all(),)

        if self.change_type == CTYPES['group']:
            return (self.grouprevisions.all(),
                    self.groupnamedetailrevisions.all(),)

        if self.change_type == CTYPES['group_relation']:
            return (self.grouprelationrevisions.all(),)

        if self.change_type == CTYPES['group_membership']:
            return (self.groupmembershiprevisions.all(),)

        if self.change_type == CTYPES['series']:
            return (self.seriesrevisions.all(),
                    self.issuerevisions.all().select_related('issue'),
                    self.issuecreditrevisions.all(),
                    self.storyrevisions.all(),
                    self.storycreditrevisions.all(),
                    self.storycharacterrevisions.all(),
                    self.storygrouprevisions.all(),
                    self.publishercodenumberrevisions.all(),
                    self.externallinkrevisions.all())

        if self.change_type == CTYPES['series_bond']:
            return (self.seriesbondrevisions.all()
                        .select_related('series_bond'),)

        if self.change_type == CTYPES['publisher']:
            return (self.publisherrevisions.all(), self.brandrevisions.all(),
                    self.indiciapublisherrevisions.all(),
                    self.externallinkrevisions.all())

        if self.change_type == CTYPES['brand']:
            return (self.brandrevisions.all(), self.branduserevisions.all(),
                    self.imagerevisions.all(),)

        if self.change_type == CTYPES['brand_group']:
            return (self.brandgrouprevisions.all(), self.brandrevisions.all(),
                    self.branduserevisions.all())

        if self.change_type == CTYPES['brand_use']:
            return (self.branduserevisions.all(),)

        if self.change_type == CTYPES['indicia_publisher']:
            return (self.indiciapublisherrevisions.all(),)

        if self.change_type == CTYPES['printer']:
            return (self.printerrevisions.all(),
                    self.indiciaprinterrevisions.all())

        if self.change_type == CTYPES['indicia_printer']:
            return (self.indiciaprinterrevisions.all(),)

        if self.change_type == CTYPES['reprint']:
            return (self.reprintrevisions.all(),)

        if self.change_type == CTYPES['image']:
            return (self.imagerevisions.all(),)

        if self.change_type == CTYPES['award']:
            return (self.awardrevisions.all(),)

        if self.change_type == CTYPES['creator']:
            return (self.creatorrevisions.all(),
                    self.datasourcerevisions.all(),
                    self.creatornamedetailrevisions.all(),
                    self.creatorartinfluencerevisions.all(),
                    self.receivedawardrevisions.all(),
                    self.creatordegreerevisions.all(),
                    self.creatormembershiprevisions.all(),
                    self.creatornoncomicworkrevisions.all(),
                    self.creatorrelationrevisions.all(),
                    self.creatorschoolrevisions.all(),
                    self.externallinkrevisions.all(),
                    )

        if self.change_type == CTYPES['creator_art_influence']:
            return (self.creatorartinfluencerevisions.all(),
                    self.datasourcerevisions.all())

        if self.change_type == CTYPES['received_award']:
            return (self.receivedawardrevisions.all(),
                    self.datasourcerevisions.all())

        if self.change_type == CTYPES['creator_degree']:
            return (self.creatordegreerevisions.all(),
                    self.datasourcerevisions.all())

        if self.change_type == CTYPES['creator_membership']:
            return (self.creatormembershiprevisions.all(),
                    self.datasourcerevisions.all())

        if self.change_type == CTYPES['creator_non_comic_work']:
            return (self.creatornoncomicworkrevisions.all(),
                    self.datasourcerevisions.all())

        if self.change_type == CTYPES['creator_relation']:
            return (self.creatorrelationrevisions.all(),
                    self.datasourcerevisions.all())

        if self.change_type == CTYPES['creator_school']:
            return (self.creatorschoolrevisions.all(),
                    self.datasourcerevisions.all())

        if self.change_type == CTYPES['creator_signature']:
            return (self.creatorsignaturerevisions.all(),
                    self.imagerevisions.all(),
                    self.datasourcerevisions.all())

        raise ValueError(
            'Changeset._revision_sets: unhandled change_type %r'
            % self.change_type)

    @property
    def revisions(self):
        """
        Fake up an iterable (not actually a list) of all revisions,
        in canonical order.
        This also iterates over freshly created revisions in one of the
        existing ones, if done in the correct order.
        """
        return itertools.chain(*self._revision_sets())

    @property
    def cached_revisions(self):
        """
        Fake up an iterable (not actually a list) of all revisions,
        in canonical order.
        Revisions are cached, this is for the queue view speed-up.
        """
        if not hasattr(self, '_save_revisions'):
            self._save_revisions = self._revision_sets()
        return itertools.chain(*self._save_revisions)

    def revision_count(self):
        return reduce(operator.add,
                      [rs.count() for rs in self._revision_sets()])

    def inline(self):
        """
        If true, edit the revisions of the changeset inline in the changeset
        page.  Otherwise, render a page for the changeset that links to a
        separate edit page for each revision.
        """
        return self.change_type in CTYPES_INLINE

    def inline_revision(self, cache_safe=False):
        if self.inline():
            if self._inline_revision is None:
                if self.change_type == CTYPES['publisher']:
                    # to filter out all the imprints in a publisher deletion
                    # changeset, probably still need this for correct handling
                    # of old revisions in change history, approved, editor_log
                    if self.publisherrevisions.count() > 1:
                        self._inline_revision = \
                            self.publisherrevisions.filter(is_master=True)[0]
                    else:
                        self._inline_revision = \
                            self.publisherrevisions.get()
                if self.change_type == CTYPES['cover']:
                    self._inline_revision = self.coverrevisions.filter()\
                                                .select_related(
                                                  'issue__series')[0]
                else:
                    if cache_safe is True:
                        return next(self.cached_revisions)
                    else:
                        self._inline_revision = next(self.revisions)
        return self._inline_revision

    def deleted(self):
        if self.inline():
            # everything but issues
            return self.inline_revision().deleted
        elif self.change_type == CTYPES['issue']:
            # single issue deletions
            return self.issuerevisions.get().deleted
        else:
            # bulk issue deletions not supported
            return False

    def editable(self):
        """
        Used for conditionals in templates, as bulk issue adds and edits as
        well as deletes cannot be edited after submission.
        """
        return (
            # TODO check creators re inline
            self.inline() or
            self.change_type in [CTYPES['issue'],
                                 CTYPES['variant_add'],
                                 CTYPES['two_issues'],
                                 CTYPES['series_bond'],
                                 CTYPES['creator'],
                                 CTYPES['creator_membership'],
                                 CTYPES['received_award'],
                                 CTYPES['creator_art_influence'],
                                 CTYPES['creator_non_comic_work']] or
            (
                self.change_type == CTYPES['issue_add'] and
                self.issuerevisions.count() == 1
            )
        ) and not self.deleted()

    def ordered_issue_revisions(self):
        """
        Used in the display.  Natural revision order must be by timestamp.
        """
        return self.issuerevisions.order_by('revision_sort_code', 'id')

    def queue_name(self):
        if self.change_type in CTYPES_BULK:
            ir_count = self.issuerevisions.count()
            if self.change_type == CTYPES['issue_bulk']:
                return str('%s and %d other issues' %
                           (self.issuerevisions.all()[0], ir_count - 1))
            if self.change_type == CTYPES['issue_add']:
                if ir_count == 1:
                    return str(self.issuerevisions.all()[0])
                elif ir_count > 1:
                    first = self.issuerevisions \
                                .order_by('revision_sort_code')[0]
                    last = self.issuerevisions \
                               .order_by('-revision_sort_code')[0]
                    return '%s %s - %s' % (first.series,
                                           first.display_number,
                                           last.display_number)
            return 'Unknown State'
        elif self.change_type == CTYPES['issue']:
            return next(self.cached_revisions).queue_name()
        elif self.change_type == CTYPES['two_issues']:
            issuerevisions = self.issuerevisions.all()
            name = issuerevisions[0].queue_name() + " and "
            if issuerevisions[0].variant_of == issuerevisions[1].issue:
                name += "base issue"
            else:
                name += issuerevisions[1].queue_name()
            return name
        elif self.change_type == CTYPES['variant_add']:
            return self.issuerevisions \
                       .get(variant_of__isnull=False).queue_name()
        elif self.change_type == CTYPES['image']:
            return self.imagerevisions.get().queue_name()
        elif self.change_type == CTYPES['series_bond']:
            return self.seriesbondrevisions.get().queue_name()
        elif self.change_type == CTYPES['creator']:
            return self.creatorrevisions.get().queue_name()
        else:
            return self.inline_revision(cache_safe=True).queue_name()

    def queue_descriptor(self):
        if self.change_type == CTYPES['issue_add']:
            return '[ADDED]'
        elif self.change_type == CTYPES['variant_add']:
            return '[VARIANT + BASE]'
        return next(self.cached_revisions).queue_descriptor()

    def changeset_action(self):
        """
        Produce a color representation of whether we're adding, removing
        or modifying data with this changeset.
        """
        if self.change_type in [CTYPES['issue_add'], CTYPES['variant_add']]:
            return ACTION_ADD
        elif self.change_type == CTYPES['issue_bulk']:
            return ACTION_MODIFY
        revision = next(self.cached_revisions)
        if revision.deleted:
            return ACTION_DELETE
        if not revision.previous_revision:
            return ACTION_ADD
        return ACTION_MODIFY

    def display_state(self):
        """
        Return the display text for the state.
        Makes it much easier to display state information in templates.
        """
        return states.DISPLAY_NAME[self.state]

    def _check_approver(self):
        """
        Check for a mentor, set to approver if necessary, and return the
        appropriate state for a submitted change.

        Set last issue even if we are part of a current series, because
        the is_current flag denotes that already and we may want to use the
        last issue to date sometimes.
        """
        if self.approver is None and (
                self.indexer.indexer.is_new and
                self.indexer.indexer.mentor is not None and
                self.change_type != CTYPES['cover'] and
                self.change_type != CTYPES['image']):
            self.approver = self.indexer.indexer.mentor

        new_state = states.PENDING
        if self.approver is not None:
            new_state = states.REVIEWING
        return new_state

    def submit(self, notes='', delete=False):
        """
        Submit changes for approval.
        If this is the first such submission or if the prior approver released
        the changes back to the general queue, then the changes go into the
        general approval queue.  If it is an edit in reply to a disapproval,
        then the changes go directly back into the approver's queue.
        """

        if (self.state != states.OPEN) and \
           not (delete and self.state == states.UNRESERVED):
            raise ErrorWithMessage(
                  "Only OPEN changes can be submitted for approval.")

        new_state = self._check_approver()

        self.comments.create(commenter=self.indexer,
                             text=notes,
                             old_state=self.state,
                             new_state=new_state)
        self.state = new_state

        # Since a submission is what puts the changeset in a non-editable
        # state, calculate the imps now.
        self.calculate_imps()
        self.save()

    def retract(self, notes=''):
        """
        Retract a submitted change.

        This can only be done if the change is not being examined.  Users
        should contact the examiner if they would like to further edit
        a change that is under examination.
        """

        if self.state != states.PENDING:
            raise ErrorWithMessage("Only PENDING changes my be retracted.")
        if self.approver is not None:
            raise ErrorWithMessage(
                  "Only changes with no approver may be retracted.")

        self.comments.create(commenter=self.indexer,
                             text=notes,
                             old_state=self.state,
                             new_state=states.OPEN)
        self.state = states.OPEN
        self.save()

    def discard(self, discarder, notes=''):
        """
        Discard a change without comitting it back to the data tables.

        This may be done either by the indexer, effectively releasign the
        reservation, or by an approver, effectively canceling it.
        """
        if self.state not in states.ACTIVE:
            raise ErrorWithMessage("Only OPEN, PENDING, DISCUSSED, or "
                                   "REVIEWING changes may be discarded.")

        self.comments.create(commenter=discarder,
                             text=notes,
                             old_state=self.state,
                             new_state=states.DISCARDED)

        self.state = states.DISCARDED
        self.save()
        for revision in self.revisions:
            if revision.source is not None:
                _free_revision_lock(revision.source)
                revision.previous_revision = None
            revision.committed = False
            revision.save()

        if self.approver:
            self.approver.indexer.add_imps(IMP_APPROVER_VALUE)

    def assign(self, approver, notes=''):
        """
        Set an approver who will examine the changes in this pending revision.

        This causes the revision to move out of the general queue and into
        the examiner's approval queue.
        """
        if self.state != states.PENDING:
            if self.state != states.REVIEWING or \
              (self.state == states.REVIEWING
               and not self.review_is_overdue()):
                raise ErrorWithMessage("Only PENDING changes can be reviewed.")

        # TODO: check that the approver has approval priviliges.
        if not isinstance(approver, User):
            raise TypeError("Please supply a valid approver.")

        self.comments.create(commenter=approver,
                             text=notes,
                             old_state=self.state,
                             new_state=states.REVIEWING)
        self.approver = approver
        self.state = states.REVIEWING
        self.save()

    def release(self, notes=''):
        if self.state not in states.ACTIVE or \
           self.approver is None:
            raise ErrorWithMessage(
                  "Only changes with an approver may be unassigned.")

        if self.state in [states.DISCUSSED, states.REVIEWING]:
            new_state = states.PENDING
        else:
            new_state = self.state

        self.comments.create(commenter=self.approver,
                             text=notes,
                             old_state=self.state,
                             new_state=new_state)
        self.approver = None
        self.state = new_state
        self.save()

    def discuss(self, commenter, notes=''):
        if self.state not in [states.OPEN, states.REVIEWING] or \
           self.approver is None:
            raise ErrorWithMessage(
                  "Only changes with an approver may be discussed.")

        self.comments.create(commenter=commenter,
                             text=notes,
                             old_state=self.state,
                             new_state=states.DISCUSSED)
        self.state = states.DISCUSSED
        self.save()

    def approve(self, notes=''):
        """
        Approve a pending index from an approver's queue into production.

        This moves the revision to approved and copies its data back to the
        production display table.
        """

        # TODO Save handling of double approvals.
        # Although we have the following check here and in the view-code, we
        # got rare double approvals, which for adds resulted in two created
        # objects. With the below if on revision.source we do have another
        # check, which will avoid double saves of objects due to the call of
        # _free_revision_lock. It is to be seen if this is now safe for adds,
        # they will get a source on the first save, but maybe the second one
        # is fast enough ? We might be able to use RevisionLock on a revision
        # for add ?
        if self.state not in [states.DISCUSSED, states.REVIEWING] or \
           self.approver is None:
            raise ErrorWithMessage(
                  "Only REVIEWING changes with an approver can be approved.")

        for revision in self.revisions:
            # TODO rethink the depency handling during committing
            #
            # We might have saved other revision due to dependencies.
            # Other types, later in the itertools.chain, are fresh,
            # but revision of the same type can became stale
            # in self.revisions, so refresh_from_db. Could do a
            # check for type, i.e. same as before, to reduce db calls.
            # save the source status before the refresh for locks ?
            source = revision.source

            revision.refresh_from_db()

            # For adds we might generate additional revisions, and call
            # commit_to_display when generating these approvals. Check
            # committed status to avoid double adds.
            # TODO check regarding stats
            # TODO revision generated later in the chain will be
            #      picked by up self.revisions anyway, so maybe not needed
            #      for purpose of avoiding double adds.
            #      But check shouldn't hurt anyway ?
            if revision.committed is not True:
                # adds have a (created) source only after commit_to_display
                if source:
                    _free_revision_lock(source)
                # first free the lock, commit_to_display might delete source
                revision.commit_to_display()

        self.comments.create(commenter=self.approver,
                             text=notes,
                             old_state=self.state,
                             new_state=states.APPROVED)

        self.state = states.APPROVED
        self.save()
        self.indexer.indexer.add_imps(self.total_imps())
        self.approver.indexer.add_imps(IMP_APPROVER_VALUE)

        # TODO remove once all type of revisions are re-factored
        for revision in self.revisions:
            revision.committed = True
            revision.save()

    def disapprove(self, notes=''):
        """
        Send the change back to the indexer for more work.
        """
        # TODO: Should we validate that a non-empty reason is supplied
        # through the approver_notes field here or in the view layer?
        # Where should validation go in general?

        if self.state not in [states.DISCUSSED, states.REVIEWING] or \
           self.approver is None:
            raise ErrorWithMessage(
              "Only REVIEWING changes with an approver can be disapproved.")
        self.comments.create(commenter=self.approver,
                             text=notes,
                             old_state=self.state,
                             new_state=states.OPEN)
        self.state = states.OPEN
        self.save()

    def review_is_overdue(self):
        if timezone.now() - timedelta(weeks=1) > self.modified:
            return True
        else:
            return False

    def calculate_imps(self):
        """
        Go through and add up the imps from the revisions, but don't commit
        to the database.
        """
        self.imps = 0
        if self.change_type in CTYPES_BULK and self.issuerevisions.count() > 1:
            # Currently, bulk changes are only allowed when the changes
            # are uniform across all revisions in the change.  When we
            # allow non-uniform changes we may need to calculate all of
            # the imp revisions and take the maximum value or something.
            self.imps += next(self.revisions).calculate_imps()
        else:
            if self.change_type == CTYPES['cover']:
                # coverrevisions can have issuerevisions and storyrevisions
                # for variant uploads, but one shouldn't get imps for them
                revisions = self.coverrevisions.all()
            else:
                revisions = self.revisions

            for revision in revisions:
                # Deletions are a bit strange.  Essentially, you get one
                # point per button you press, however many objects that
                # button deletes.  Similar to bulk adds counting the same
                # as a single add.  Story objects are deleted one at a time,
                # and multiple of them can be deleted in a single changeset
                # without deleting the entire issue.  Issue and other objects,
                # however, are only deleted when the entire action of the
                # changeset is a deletion.  So they get one IMP_DELETE no
                # matter what else was in the changeset.

                if revision.deleted:
                    from apps.oi.models import (
                        StoryRevision, StoryCreditRevision, IssueCreditRevision,
                        ReprintRevision, CharacterNameDetailRevision,
                        CreatorNameDetailRevision, DataSourceRevision,
                        StoryCharacterRevision, StoryGroupRevision)
                    if isinstance(revision, StoryRevision) or \
                       isinstance(revision, StoryCreditRevision) or \
                       isinstance(revision, IssueCreditRevision) or \
                       isinstance(revision, ReprintRevision) or \
                       isinstance(revision, CharacterNameDetailRevision) or \
                       isinstance(revision, CreatorNameDetailRevision) or \
                       isinstance(revision, DataSourceRevision) or \
                       isinstance(revision, StoryCharacterRevision) or \
                       isinstance(revision, StoryGroupRevision):
                        self.imps += IMP_DELETE
                    else:
                        self.imps = IMP_DELETE
                        return
                else:
                    self.imps += revision.calculate_imps()

    def magnitude(self):
        """
        A rough guide to the size of the change.  Currently implemented by
        examining the calculated imps, but may be switched to a changed field
        count of some sort if we change how imps work or decide that a
        different metric will work better as a size estimate.  For instance
        number of characters (as in letters, not the characters field) changed.
        """
        return self.imps

    def total_imps(self):
        """
        The total number of imps awarded for this changeset, including both
        field-calculated imps and bonuses such as the add bonus.
        """
        calculated = self.imps
        if self.change_type != CTYPES['cover'] and \
           self.change_type != CTYPES['image'] and \
           self.changeset_action() == ACTION_ADD:
            return calculated + IMP_BONUS_ADD
        return calculated

    def __str__(self):
        if self.inline():
            return str(self.inline_revision())
        if self.change_type in CTYPES_BULK:
            return self.queue_name()
        if self.change_type == CTYPES['issue']:
            return str(self.issuerevisions.all()[0])
        if self.change_type == CTYPES['two_issues']:
            return self.queue_name()
        if self.change_type == CTYPES['variant_add']:
            return self.queue_name() + ' [Variant]'
        if self.id:
            return 'Changeset: %d' % self.id
        return "Changeset"


class ChangesetComment(models.Model):
    """
    Comment class for revision management.

    We are not using Django's comments contrib package for several reasons:

    1.  Additional fields- we want to associate comments with state
        transitions, which also tells us who made the comment (since
        currently comments can only be made by the person changing the
        revision state, or by the indexer when saving intermediate edits.

        TODO: The whole bit where the indexer can end up tacking on a bunch
        of comments rather than having just one that they build up and edit
        and send in with the submission is not quite right.  Needs work still.

    2.  We don't need the anti-spam measures as these will not be accessible
        by the general public.  If we get a spammer with an account we'll have
        bigger problems than comments, and other ways to deal with them.

    3.  Unneeded fields.  This isn't really an obstacle to use, but the
        django comments system copies over a number of fields that we would
        not want copied in case they change (email, for instance).
    """
    class Meta:
        db_table = 'oi_changeset_comment'
        ordering = ['created']
        get_latest_by = "created"

    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    changeset = models.ForeignKey(Changeset, on_delete=models.CASCADE,
                                  related_name='comments')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=True)
    revision_id = models.IntegerField(db_index=True, null=True)
    revision = GenericForeignKey('content_type', 'revision_id')

    old_state = models.IntegerField()
    new_state = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def display_old_state(self):
        return states.DISPLAY_NAME[self.old_state]

    def display_new_state(self):
        return states.DISPLAY_NAME[self.new_state]


def _get_revision_lock(object, changeset=None):
    try:
        with transaction.atomic():
            revision_lock = RevisionLock.objects.create(locked_object=object,
                                                        changeset=changeset)
    except IntegrityError:
        revision_lock = None
    return revision_lock


def _free_revision_lock(object):
    # filter().delete() is idempotent: freeing an already-freed lock is a
    # no-op rather than a DoesNotExist, which matters on retried commits.
    with transaction.atomic():
        RevisionLock.objects.filter(
          object_id=object.id,
          content_type=ContentType.objects.get_for_model(object)).delete()


def _removed_related_objects(removed_objects, source_type):
    for removed_object in removed_objects:
        cd = removed_object.cleaned_data
        if 'id' in cd and cd['id']:
            if getattr(removed_object.cleaned_data['id'], source_type):
                removed_object.cleaned_data['id'].deleted = True
                removed_object.cleaned_data['id'].save()
            else:
                removed_object.cleaned_data['id'].delete()


def _process_formset(self, formset, revision_type=None, generic=False):
    for form in formset:
        if form.is_valid() and form.cleaned_data \
           and form not in formset.deleted_forms:
            cd = form.cleaned_data
            if 'id' in cd and cd['id']:
                form.save()
            else:
                revision = form.save(commit=False)
                kwargs = {}
                if generic:
                    content_type = ContentType.objects.get_for_model(self)
                    kwargs['content_type'] = content_type
                    kwargs['object_id'] = self.id
                else:
                    kwargs[revision_type] = self

                revision.save_added_revision(changeset=self.changeset,
                                             **kwargs)
        elif (not form.is_valid() and form not in formset.deleted_forms):
            raise ValueError


class RevisionLock(models.Model):
    """
    Indicates that a particular Changeset has a particular row locked.

    In order to have an active Revision for a given row, a Changeset
    must hold a lock on it.  Rows in this table represent locks,
    and the unique_together constraint on the content type and object id
    ensure that only one Changeset can hold an object's lock at a time.
    Locks are released by deleting the row.

    A lock with a NULL changeset is used to check that the object can
    be locked before creating a Changeset that would not be used
    if the lock fails.

    TODO: cron job to periodically scan for stale locks?
    """
    class Meta:
        db_table = 'oi_revision_lock'
        unique_together = ('content_type', 'object_id')

    changeset = models.ForeignKey(Changeset, on_delete=models.CASCADE,
                                  null=True,
                                  related_name='revision_locks')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField(db_index=True)
    locked_object = GenericForeignKey('content_type', 'object_id')


class RevisionManager(models.Manager):
    """
    Custom manager base class for revisions.
    """
    # We want to use these methods on reverse relation sets.
    use_for_related_fields = True

    def get_queryset(self):
        return RevisionQuerySet(self.model, using=self._db)

    def active(self):
        """
        Get the active revision, assuming that there is one.

        Throws the DoesNotExist or MultipleObjectsReturned exceptions on
        the appropriate Revision subclass, as it calls get() underneath.
        """
        return self.active_set().get()

    def active_set(self):
        """
        Get the active revision as a query set, which might be empty.

        Currently we do not expect multiple active revisions.
        """
        return self.filter(changeset__state__in=states.ACTIVE)

    def pending_deletions(self):
        """
        Filter to active revisions that are deleting their object.
        """
        return self.active_set().filter(deleted=True)

    def filter_pending_deletions(self, data_queryset):
        """
        Filter pending deletions out of a queryset of GcdBase-derived objects.

        Since this does not operate on Revision querysets, it should not be
        copied to the RevisionQuerySet class.
        """
        return data_queryset.exclude(
            revisions__deleted=True,
            revisions__changeset__state__in=states.ACTIVE).distinct()

    # H. TODO deprecated
    def _clone_revision(self, instance, instance_class,
                        changeset, check=True, **kwargs):
        """
        Given an existing instance, create a new revision based on it.

        This new revision will be where the edits are made.
        If there are no revisions, first save a baseline so that the pre-edit
        values are preserved.
        Entirely new publishers should be started by simply instantiating
        a new PublisherRevision directly.
        """
        if not isinstance(instance, instance_class):
            raise TypeError("Please supply a valid %s." % instance_class)

        revision = self._do_create_revision(instance,
                                            changeset=changeset,
                                            **kwargs)

        # Link to the previous revision for the data object.
        # It is an error not to have a previous revision for
        # a pre-existing data object.
        previous_revision = type(revision).objects.get(
                            next_revision=None,
                            changeset__state=states.APPROVED,
                            committed=True,
                            **{revision.source_name: instance})
        revision.previous_revision = previous_revision
        revision.save()

        return revision


class RevisionQuerySet(models.QuerySet):
    """
    Propagates the RevisionManager methods to further querysets.
    """
    def active(self):
        return self.get(changeset__state__in=states.ACTIVE)

    def active_set(self):
        return self.filter(changeset__state__in=states.ACTIVE)

    def pending_deletions(self):
        return self.active_set().filter(deleted=True)


class Revision(models.Model):
    """
    Abstract base class implementing the workflow of a revisable object.

    This holds the data while it is being edited, and remains in the table
    as a history of each given edit, including those that are discarded.

    A state column trackes the progress of the revision, which should
    eventually end in either the APPROVED or DISCARDED state.

    Various classmethods exist to get information about the revision fields
    so that they can be handled generically.  All of these method names
    start with _get and end with a suffix indicating the return value:

    fields:       a dictionary mapping field attribute names to field objects
    field_names:  a set of field attribute names
    field_tuples: a set of tuples of attribute names that may cross relations
    """
    class Meta:
        abstract = True

    objects = RevisionManager()

    changeset = models.ForeignKey(Changeset, on_delete=models.CASCADE,
                                  related_name='%(class)ss')
    previous_revision = models.OneToOneField('self', on_delete=models.CASCADE,
                                             null=True,
                                             related_name='next_revision')

    # If True, this revision deletes the object in question.  Other fields
    # should not contain changes but should instead be a record of the object
    # at the time of deletion and therefore match the previous revision.
    # If changes are present, then they were never actually published and
    # should be ignored in terms of history.
    deleted = models.BooleanField(default=False, db_index=True)

    # If True, this revision has been committed back to the display tables.
    # If False, this revision will never be committed.
    # If None, this revision is still active, and may or may not be committed
    # at some point in the future.
    committed = models.BooleanField(default=None, null=True, db_index=True)

    comments = GenericRelation(ChangesetComment,
                               content_type_field='content_type',
                               object_id_field='revision_id')

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    is_changed = False

    # These are initialized on first use- see the corresponding classmethods.
    # Set to None as an empty iterable is a valid possible value.
    _regular_fields = None
    _irregular_fields = None
    _single_value_fields = None
    _multi_value_fields = None
    _meta_fields = None

    # Child classes must set these properly.  Unlike source, they cannot be
    # instance properties because they are needed during revision construction.
    # H.TODO source_name = NotImplementedError
    source_class = NotImplementedError
    # H.TODO no separate _get_source

    @property
    def source(self):
        """
        The thing of which this is a revision.
        Since this is different for each revision,
        the subclass must override this.
        """
        # Call separate method for polymorphism
        return self._get_source()

    def _get_source(self):
        raise NotImplementedError

    @property
    def source_name(self):
        """
        Used to key lookups in various shared view methods.
        """
        # Call separate method for polymorphism
        return self._get_source_name()

    def _get_source_name(self):
        raise NotImplementedError

    @source.setter
    def source(self, value):
        """
        Used with source_class by base revision code to create new objects.
        """
        raise NotImplementedError

    # #####################################################################
    # Properties indicating the type of action this Revision is performing.
    @property
    def added(self):
        """
        True if this is an open or committed add.
        """
        return not self.previous_revision and not self.discarded

    @property
    def edited(self):
        """
        True if this open or committed and neither an add nor a delete.
        NOTE: This does not necessarily mean there have been any edits.
        """
        return bool(self.previous_revision and not
                    (self.deleted or self.discarded))

    @property
    def discarded(self):
        """
        For symmetry with committed and open.
        """
        return self.committed is False

    @property
    def open(self):
        """
        For symmetry with committed and discarded.
        """
        return self.committed is None

    # #####################################################################
    # Field declarations and classification.

    @classmethod
    def _classify_fields(cls):
        """
        Populates the regular and irregular field dictionaries.

        This should be called at most once during the life of the class.
        It relies on the excluded field set to filter out irrelevant fields.
        """
        if cls._regular_fields is not None:
            # Already classified.
            return

        # NOTE: As of Django 1.9, reverse relations show up in the list
        #       of fields, but are not actually Field instances.  Since
        #       we don't want them anyway, use this to filter them out.
        #
        #       In a future release of Django this will change, but should
        #       be covered in the release notes.  And presumably there
        #       will be a different reliable way to filter them out.
        excluded_names = cls._get_excluded_field_names()
        meta_names = cls._get_meta_field_names()
        # TODO: use OrderedDict after update to python 3, that should allow
        # an automatic way to generate an ordered field_list per model
        data_fields = {
            f.get_attname(): f
            for f in cls.source_class._meta.get_fields()
            if isinstance(f, Field) and f.get_attname() not in excluded_names
        }
        rev_fields = {
            f.get_attname(): f
            for f in cls._meta.get_fields()
            if isinstance(f, Field) and f.get_attname() not in excluded_names
        }
        cls._regular_fields = {}
        cls._irregular_fields = {}
        cls._single_value_fields = {}
        cls._multi_value_fields = {}
        cls._meta_fields = {}

        for name, data_field in data_fields.items():
            # Currently we do not have relations that are meta fields,
            # so just handle those here and move on to the next field.
            if name in meta_names:
                cls._meta_fields[name] = data_field
                continue

            # Note that ForeignKeys and OneToOneFields show up under the
            # attribute name for the actual key ('parent_id' instead of
            # 'parent'), so strip the _id off for more convenient use.
            # You can still pass the 'parent' form to _meta.get_field().
            # TODO: Is there a more reliable way to do this?  Cannot
            #       seem to find anything in the Django 1.9 API.
            key_name = name
            if ((data_field.many_to_one or data_field.one_to_one) and
                    name.endswith('_id')):
                # If these aren't the same we have no idea what's going
                # on, so an AssertionError is appropriate.
                assert cls.source_class._meta.get_field(key_name) == data_field
                key_name = name[:-len('_id')]

            if name not in rev_fields:
                # No corresponding revision field, so it can't be regular.
                cls._irregular_fields[key_name] = data_field
                continue

            # The internal type is the field type i.e. CharField or ForeignKey.
            rev_field = rev_fields[name]
            rev_ftype = rev_field.get_internal_type()
            data_ftype = data_field.get_internal_type()
            rev_target = (rev_field.target_field.get_attname()
                          if isinstance(rev_field, related.RelatedField)
                          else None)
            data_target = (data_field.target_field.get_attname()
                           if isinstance(data_field, related.RelatedField)
                           else None)

            if rev_ftype == data_ftype and rev_target == data_target:
                # Non-relational fields have a .rel of None.  While we should
                # never have identically named foreign keys that point to
                # different things, it's better to check than assume.
                #
                # Most of these fields can be copied, including ManyToMany
                # fields, although ManyToMany fields may need to be treated
                # differently in other ways, so we track them separately
                # as well.
                cls._regular_fields[key_name] = data_field

                if data_field.many_to_many or data_field.one_to_many:
                    cls._multi_value_fields[key_name] = data_field
                else:
                    cls._single_value_fields[key_name] = data_field

            elif isinstance(data_field,
                            TaggableManager) and name == 'keywords':
                # Keywords are regular but not assignable in the same way
                # as single- or multi-value fields as the keywords are
                # stored as a single string in revisions.
                cls._regular_fields[key_name] = data_field

            else:
                # There's some mismatch, so we don't know how to handle this.
                cls._irregular_fields[key_name] = data_field

    @classmethod
    def _get_excluded_field_names(cls):
        """
        Field names that appear to be regular fields but should be ignored.

        Any data object field that has a matching (name, type, and if
        relevant related type) field on the revision that should *NOT*
        be copied back and forth should be included here.

        It is not necessary to include non-matching fields here, whether
        they affect revision field values or not.

        Fields listed here may or may not be present on any given data object,
        but if they are present they should be omitted from automatic
        classification.

        Subclasses may add to this set, but should never remove fields from it.

        Deprecated fields should NOT be included, as they should continue
        to be copied back and forth until the data is all removed, at
        which point the field should be dropped from the data object.
        """
        # Not all data objects have all of these, but since this
        # is just used in set subtractions, that is safe to do.
        # All of these fields are common to multiple revision types.
        #
        # id, created, and modified are automatic columns
        # tagged_items is the reverse relation for 'keywords'
        # image_resources are handled through their own ImageRevisions
        return frozenset({
            'id',
            'created',
            'modified',
            'deleted',
            'tagged_items',
            'image_resources',
        })

    @classmethod
    def _get_deprecated_field_names(cls):
        """
        The set of field names that should not be allowed in new objects.

        These fields are still present in both the data object and revision
        tables, and should therefore be copied out of the data objects in
        case old values are still present and need to be preserved until
        they can be migrated.  But new values should not be allowed.
        """
        return frozenset()

    @classmethod
    def _get_meta_field_names(cls):
        """
        Fields that are about other fields, and only copied from rev to data.

        These fields are not included in either the regular or irregular
        field sets, nor the single value or multi value sets.  They are
        handled completely separately.

        See also _get_meta_fields() for more information.
        """
        return frozenset()

    @classmethod
    def _get_regular_fields(cls):
        """
        Data fields that can be predictably transferred to and from revisions.

        For most fields, this just means copying the value.  For a few
        such as keywords, there is a different but standard way of transferring
        the values.  For ManyToManyFields, the add/remove/set/clear methods
        can be used.
        """
        cls._classify_fields()
        return cls._regular_fields

    @classmethod
    def _get_irregular_fields(cls):
        """
        Data object fields that cannot be handled by generic revision code.

        These fields either don't exist on the revision, or they do not
        match types and we do not understand the mismatch as a well-known
        special case (i.e. keywords as CharField vs TaggableManager).
        """
        cls._classify_fields()
        return cls._irregular_fields

    @classmethod
    def _get_single_value_fields(cls):
        """
        The subset of regular fields that have a single value.
        """
        cls._classify_fields()
        return cls._single_value_fields

    @classmethod
    def _get_multi_value_fields(cls):
        """
        The subset of regular fields that have a queryset value.
        """
        cls._classify_fields()
        return cls._multi_value_fields

    @classmethod
    def _get_meta_fields(cls):
        """
        Fields that are not managed as primary data.

        These fields are usually meta-data of some sort, such as flags
        indicating data that needs revisiting.  Alternatively, they
        may be additional information calculated from primary data
        but cached in database fields.

        These field values may be changed in the data object without
        using a Revision, and Revisions should not attempt to keep
        them in sync.

        When committing a revision, the field must be activley set
        correctly as it is not copied *from* the data object, but
        will be copied back *to* it.

        Note that fields that are calculated either entirely within
        the revision, or entirely within the data object, but are
        never copied in either direction should *not* be included
        here.  This classification is essentially for fields that
        are only copied from revision to data object.
        """
        cls._classify_fields()
        return cls._meta_fields

    @classmethod
    def _get_conditional_field_tuple_mapping(cls):
        """
        A dictionary of field names mapped to their conditions.

        The conditions are stored as a tuple of field names that can
        be applied to an instance to get the value.
        For example, ('series', 'has_isbn') would mean that you
        could get the value by looking at revision.series.has_isbn
        """
        return {}

    @classmethod
    def _get_parent_field_tuples(cls):
        """
        The set of parent-ish objects that this revision may need to update.

        This should include parent chains up to the root data object(s) that
        need updating, for instance an issue should include its publisher
        by way of the series foreign key (as opposed to publishers found
        through other links, which are either duplicate or should be
        ignored.

        Elements of the set are tuples to allow for multiple parent levels.
        ForeignKey, ManyToManyField, and OneToOneField are all valid
        field types for this method.

        Note that if multiple parents along a path require updating, then
        each level of parent must be included.  In the issue example,
        ('series',) and ('series', 'publisher') must both be included.

        This allows for the case where an intermediate object does not
        require updating.
        """
        return frozenset()

    @classmethod
    def _get_major_flag_field_tuples(cls):
        """
        The set of flags that require further processing upon commit.

        These are stored as tuples in the same way as
        _get_parent_field_tuples().
        """
        return frozenset()

    @classmethod
    def _get_stats_category_field_tuples(cls):
        """
        These fields, when present, determine CountStats categories to update.

        This implementation works for any class that does not have to get
        these fields from a parent object.
        """
        stats_tuples = set()
        for name in ('country', 'language'):
            try:
                # We just call get_field to see if it raises, so we
                # ignore the return value.
                cls._meta.get_field(name)
                stats_tuples.add((name,))
            except FieldDoesNotExist:
                pass

        return stats_tuples

    # #####################################################################
    # Methods for creating (cloning) a Revision from a data object,
    # including hook methods for use in customizing the cloning process.

    def _pre_initial_save(self, fork=False, fork_source=None,
                          exclude=frozenset(), **kwargs):
        """
        Called just before saving to the database to handle unusual fields.

        Note that if there is a source data object, it will already be set.

        See clone() for usage of fork, fork_source, and exclude.
        """
        pass

    def _post_m2m_add(self, fork=False, fork_source=None, exclude=frozenset()):
        """
        Called after initial save to database and m2m population.

        This is for handling unusual fields that require the revision to
        already exist in the database.

        See clone() for usage of fork, fork_source, and exclude.
        """
        pass

    @classmethod
    def clone(cls, data_object, changeset, fork=False, exclude=frozenset(),
              **kwargs):
        """
        Given an existing data object, create a new revision based on it.

        This new revision will be where the edits are made.

        'fork' may be set to true to create a revision for a new data
        object based on an existing data object.  The source and
        previous_revision fields will be left null in this case.  Due to
        this, the source will be passed separately to the customization
        methods as 'fork_source'.

        Entirely new data objects should be started by simply instantiating
        a new revision of the appropriate type directly.

        A set (or set-like object) of field names to exclude from copying
        may be passed.  This is particularly useful for forking.
        """
        # Guard against exclude names that are not fields on either the
        # revision or its data object. Such a name silently does nothing (the
        # set subtraction is a no-op), which is exactly how a renamed field
        # slips through -- e.g. excluding 'brand' after it became the
        # 'brand_emblem' m2m. Data-object field names are allowed too because
        # some (like 'on_sale_date') exist on the source but are split across
        # different fields on the revision.
        def _field_names(model_class):
            fields = model_class._meta.get_fields()
            return ({f.name for f in fields} |
                    {f.get_attname() for f in fields if isinstance(f, Field)})

        known_field_names = _field_names(cls) | {'keywords'}
        if cls.source_class is not NotImplementedError:
            known_field_names |= _field_names(cls.source_class)
        unknown = set(exclude) - known_field_names
        if unknown:
            raise ValueError(
                '%s.clone() was given exclude names that are not fields: %s'
                % (cls.__name__, sorted(unknown)))

        # We start with all assignable fields, since we want to copy
        # old values even for deprecated fields.
        rev_kwargs = {field: getattr(data_object, field)
                      for field
                      in set(cls._get_single_value_fields()) - exclude}

        # Keywords are not assignable but behave the same way whenever
        # they are present, so handle them here.
        if 'keywords' in set(cls._get_regular_fields()) - exclude:
            rev_kwargs['keywords'] = get_keywords(data_object)

        # Instantiate the revision.  Since we do not know the exact
        # field name for the data_object, set it through the source property.
        revision = cls(changeset=changeset, **rev_kwargs)

        if data_object and not fork:
            revision.source = data_object

            # Link to the previous revision for this data object.
            # It is an error not to have a previous revision for
            # a pre-existing data object.
            previous_revision = type(revision).objects.get(
                next_revision=None,
                changeset__state=states.APPROVED,
                **{revision.source_name: data_object})
            revision.previous_revision = previous_revision

        revision._pre_initial_save(fork=fork, fork_source=data_object,
                                   exclude=exclude, **kwargs)

        revision.save()

        # Populate all of the many to many relations that don't use
        # their own separate revision classes.
        for m2m in set(revision._get_multi_value_fields()) - exclude:
            getattr(revision, m2m).add(*list(getattr(data_object, m2m).all()))
        revision._post_m2m_add(fork=fork, fork_source=data_object,
                               exclude=exclude)

        return revision

    # ##################################################################
    # Methods for inventorying significant changes to the fields,
    # an handling those changes and the resulting updates to cached
    # values and statistics.

    def _reset_values(self):
        pass

    def _check_major_change(self, attrs):
        """
        Fill out the changes structure for a single attribute tuple.
        """
        old, new = self.source, self
        changes = {}

        # The name of the last foreign key is the name used for
        # tracking changes.  Except 'parent' is tracked as 'publisher'
        # for historical reasons.  Eventually we will likely switch
        # the 'parent' database fields to 'publisher'.
        name = 'publisher' if attrs[-1] == 'parent' else attrs[-1]

        old_rp = relpath.RelPath(self.source_class, *attrs)
        new_rp = relpath.RelPath(type(self), *attrs)

        old_value = old_rp.get_value(old, empty=self.added)
        new_value = new_rp.get_value(new, empty=self.deleted)
        multi_valued = old_rp.multi_valued
        boolean_valued = old_rp.boolean_valued

        changed = '%s changed' % name
        if self.added or self.deleted:
            changes[changed] = True
        elif multi_valued:
            # Different QuerySet objects are never equal, even if they
            # express the same queries and have the same evaluation state.
            # So use sets for determining changes.
            changes[changed] = set(old_value) != set(new_value)
        else:
            changes[changed] = old_value != new_value

        if boolean_valued:
            # We only care about the direction of change for booleans.
            # At this time, it is sufficient to treat None for a NullBoolean
            # as False.  This can produce a "changed" (False to or from None)
            # in which both "to" and "from" are False.  Strange but OK.
            #
            # Without the bool(), if old_value (for from) or new_value
            # (for to) are None, then the changes would be set to None
            # instead of True or False.
            changes['to %s' % name] = bool((not old_value) and new_value)
            changes['from %s' % name] = bool(old_value and (not new_value))
        else:
            changes['old %s' % name] = old_value
            changes['new %s' % name] = new_value

        return changes

    def _get_major_changes(self, extra_field_tuples=frozenset()):
        """
        Returns a dictionary for deciding what additional actions are needed.

        Major changes are generally ones that require updating statistics
        and/or cached counts in the display tables.  They may also require
        other actions.

        This method bundles up all of the flags and old vs new values
        needed for easy conditionals and easy calls to update_all_counts().

        extra_field_tuples is a way for child classes to put additional fields
        into the changes dictionary through a super() call without having
        to put them in any of the sets that trigger special handling.
        This is useful for oddball fields that trigger custom code when
        changed, but don't fall into any of the usual patterns.
        """
        changes = {}
        for name_tuple in (self._get_parent_field_tuples() |
                           self._get_major_flag_field_tuples() |
                           self._get_stats_category_field_tuples() |
                           extra_field_tuples):
            changes.update(self._check_major_change(name_tuple))
        return changes

    def _adjust_stats(self, changes, old_counts, new_counts):
        """
        Handles universal statistics updating.

        Child classes should call this with super() before proceeding
        to adjust counts stored in their display objects.
        """
        if self.source_class._update_stats and (old_counts != new_counts or
                                                changes.get('country changed',
                                                            False) or
                                                changes.get('language changed',
                                                            False)):
            CountStats.objects.update_all_counts(
                old_counts,
                country=changes.get('old country', None),
                language=changes.get('old language', None),
                negate=True)
            CountStats.objects.update_all_counts(
                new_counts,
                country=changes.get('new country', None),
                language=changes.get('new language', None))

        deltas = {
            k: new_counts.get(k, 0) - old_counts.get(k, 0)
            for k in set(old_counts) | set(new_counts)
        }
        if any(deltas.values()) or True in list(changes.values()):
            for parent_tuple in self._get_parent_field_tuples():
                self._adjust_parent_counts(parent_tuple, changes, deltas,
                                           old_counts, new_counts)

            fields = self.source.update_cached_counts(deltas)
            if fields:
                self.source.save(update_fields=fields)

    def _adjust_parent_counts(self, parent_tuple, changes, deltas,
                              old_counts, new_counts):
        """
        Handles the counts adjustment for a single parent.
        """
        # Always use the last attribute name for the parent name.
        # But switch 'parent' to 'publisher' (historical reasons).
        parent = (
            'publisher' if parent_tuple[-1] == 'parent' else parent_tuple[-1])

        changed = changes['%s changed' % parent]
        old_value = changes['old %s' % parent]
        new_value = changes['new %s' % parent]

        multi = relpath.RelPath(type(self), *parent_tuple).multi_valued

        if changed:
            if old_value:
                if multi:
                    for v in old_value:
                        fields = v.update_cached_counts(old_counts, negate=True)
                        if fields:
                            v.save(update_fields=fields)
                else:
                    fields = old_value.update_cached_counts(old_counts,
                                                            negate=True)
                    if fields:
                        old_value.save(update_fields=fields)
            if new_value:
                if multi:
                    for v in new_value:
                        fields = v.update_cached_counts(new_counts)
                        if fields:
                            v.save(update_fields=fields)
                else:
                    fields = new_value.update_cached_counts(new_counts)
                    if fields:
                        new_value.save(update_fields=fields)

        elif old_counts != new_counts:
            # Doesn't matter whether we use old or new as they are the same.
            if multi:
                for v in new_value:
                    fields = v.update_cached_counts(deltas)
                    if fields:
                        v.save(update_fields=fields)
            else:
                fields = new_value.update_cached_counts(deltas)
                if fields:
                    new_value.save(update_fields=fields)

    # #####################################################################
    # Methods for processing the indexer edits, in particular involving
    # several forms.

    def extra_forms(self, request):
        """
        Fetch additional forms of other/related objects for editing.
        """
        return {}

    @classmethod
    def extra_forms_errors(cls, request, form, extra_forms):
        """
        Process additional forms for errors when validation failed.
        """
        pass

    def process_extra_forms(self, extra_forms):
        """
        Process additional forms of other/related objects on save.
        """
        pass

    def post_form_save(self):
        """
        Runs just after the revision and extra forms are saved.

        Handles connection between forms and between fields.
        """
        pass

    # #####################################################################
    # Methods for saving the Revision back to the data object, including
    # hook methods for customizing that process.

    def _pre_commit_check(self):
        """
        Runs sanity checks before anything else in commit_to_display.

        This method must not attempt to change anything, and should raise
        an exception if the check fails.  For conditions that can be
        fixed, use _handle_prerequisites.
        """
        pass

    def _handle_prerequisites(self, changes):
        """
        Creates/commits related revisions before committing this revision.

        This is where a revision subclass should look for other revisions
        that must be committed before the commit of this revision can
        proceed.  It should create and/or commit those prerequisite
        revisions as needed, updating this revision with the results
        if appropriate.

        This method should take into account the possibility that multiple
        revisions in a given changeset may have the same prerequisites, and
        either only perform actions that can be safely repeated or verify
        that prior revisions have not already handled things.

        This runs before the old stat counts are collected so that any
        changes from the prerequisites are accounted for in the stats,
        any any count updates are not double-counted.

        Note that prerequisite revisions may attempt to handle this
        revision as a dependent revision, so care must be taken to
        avoid loops.
        """
        pass

    def _pre_delete(self, changes):
        """
        Runs just before the data object is deleted in a deletion revision.
        """
        # for models of type GcdLink we need to clear the source info in
        # all revisions since the link object gets deleted
        #
        # TODO many models of this type have this routine as well, likely
        # not needed but an oversight during re-factor of these models ?
        # These models set directly to None the field that is referred
        # to as source, which seems to be doing the same thing as setting
        # self.source to None here. Double check.
        if GcdLink in type(self.source).mro():
            for revision in self.source.revisions.all():
                setattr(revision, 'source', None)
                revision.save()
            self.source = None
        pass

    def _post_create_for_add(self, changes):
        """
        Runs after a new object is created during an add.

        This is where things like adding many-to-many objects can be done.
        """
        pass

    def _post_assign_fields(self, changes):
        """
        Runs once the added or edited display object is set up.

        Fields that can't be copied directly are handled here.
        Not run for deletions.
        """
        pass

    def _pre_save_object(self, changes):
        """
        Runs just before the display object is saved.

        This is where additional processing related to the major changes,
        such as conditional field adjustments, can be done.
        """
        pass

    def _post_save_object(self, changes):
        """
        Runs just after the display object is saved.

        Typically used to handle many-to-many fields.
        """
        pass

    def _handle_dependents(self, changes):
        """
        Creates/commits related revisions after committing this revision.

        This is where a revision subclass should ensure that any revisions
        that depend on this revision get handled created and/or committed
        appropriately.

        This runs at the very end of commit_to_display(), after the new
        stats have been collected and handled.  Otherwise any counts
        adjusted in the revisions handled here would be double-counted
        by this revision's stats code as well.

        Note that dependent revisions may attempt to handle this revision
        as a prerequisite, so care must be taken to avoid loops.
        To help with this, self.committed will be set to True and this
        revision will be saved to the database by the time this method
        is called.
        """
        pass

    def _handle_dependent_image_revision(self):
        """
        align image from ModelRevision to Model
        """
        if self.changeset.imagerevisions.count():
            image_revision = self.changeset.imagerevisions.get()
            content_type = ContentType.objects.get_for_model(self.source)
            image_revision.object_id = self.source.id
            image_revision.content_type = content_type
            image_revision.save()

    def _copy_fields_to(self, target):
        """
        Used to copy fields from a revision to a display object.

        At the time when this is called, the revision may not yet have
        the display object set as self.source (in the case of a newly
        added object), so the target of the copy is given as a parameter.
        """
        fields_to_copy = self._get_single_value_fields().copy()
        fields_to_copy.update(self._get_meta_fields())
        c = self._get_conditional_field_tuple_mapping()
        for name in fields_to_copy:
            # If conditional, apply getattr until we produce the flag
            # value and only assign the field if that flag is True.
            if (name not in c or reduce(getattr, c[name], self)):
                setattr(target, name, getattr(self, name))

    def commit_to_display(self, clear_reservation=True):
        """
        Writes the changes from the revision back to the display object.

        Revisions should handle their own dependencies on other revisions.
        """
        self._pre_commit_check()
        changes = self._get_major_changes()

        self._handle_prerequisites(changes)
        old_stats = {} if self.added else self.source.stat_counts()

        if self.deleted:
            deleted_source = self.source
            self._pre_delete(changes)
            self._reset_values()
        else:
            if self.added:
                self.source = self.source_class()
                self._post_create_for_add(changes)

            self._copy_fields_to(self.source)
            self._post_assign_fields(changes)

        self._pre_save_object(changes)
        # Deletes of links are 'real', the source_id is reset in _pre_delete.
        # Some deletes therefore do not have self.source anymore.
        # It might be fine to just check self.deleted, but some sources
        # might need to be saved on a delete ?
        if not self.deleted or self.source:
            self.source.save()

        if self.added:
            # Reset the source because now it has a database id,
            # which we must save.  Just saving the added source while
            # it is attached does not update the revision with the newly
            # created source id from the database.
            #
            # We do this because it is easier for all other code if it
            # only works with self.source, no matter whether it is
            # an add, edit, or delete.
            # TODO refresh_from_db instead ?
            self.source = self.source

        self.committed = True
        self.save()

        # Keywords must be handled post-save for added objects, and
        # are safe to handle here for other types of revisions.
        if 'keywords' in self._get_regular_fields():
            save_keywords(self, self.source)

        for multi in self._get_multi_value_fields():
            old_rp = relpath.RelPath(type(self), multi)
            new_rp = relpath.RelPath(type(self.source), multi)
            new_rp.set_value(self.source, old_rp.get_value(self))

        self._post_save_object(changes)
        if self.deleted:
            deleted_source.delete()
        # some source objects get deleted, but these do not have stats
        if self.source:
            new_stats = self.source.stat_counts()
            self._adjust_stats(changes, old_stats, new_stats)
        self._handle_dependents(changes)

    # #####################################################################
    # Methods not involved in the Revision lifecycle.

    def __str__(self):
        """
        String representation for debugging purposes only.

        No UI should rely on this representation being suitable for end users.
        """
        # It's possible to add and delete something at the same time,
        # although we don't currently allow it.  In theory one could
        # edit and delete, although we don't even have any way to indicate
        # that currently.
        action = []
        if self.added:
            action.append('adding')
        if self.edited:
            action.append('editing')
        if self.deleted:
            action.append('deleting')

        return '%r %s %s %r (%r) change %r' % (
            self.id,
            ' & '.join(action),
            self.source_class.__name__,
            self.source,
            None if self.source is None else self.source.id,
            None if self.changeset_id is None else self.changeset_id,
        )

    # #####################################################################
    # Old methods. t.b.c, if deprecated.

    def _changed(self):
        """
        The dictionary of change information between this revision and the
        previous revision of the same source object.
        """
        pass

    def field_list(self):
        """
        Public field list interface, in case we ever decide we want
        to process child class field lists before returning them.
        """
        return self._field_list()

    def _field_list(self):
        """
        Default implementation for objects that have no fields (like covers).
        """
        return []

    def _get_blank_values(self):
        """
        Create a dictionary with the "blank" values for all of the fields
        of this type of revision.  This is used to determine the change
        value of newly added objects.  Blank values are often not allowed
        in the database (i.e. NOT NULL columns) so this cannot be done
        with a revision instance.  Blank values should be set.
        """
        raise NotImplementedError

    def previous(self):
        # We never spontaneously gain a previous revision during normal
        # operation, so it's safe to cache this.
        if hasattr(self, '_prev_rev'):
            return self._prev_rev

        self._prev_rev = self.previous_revision

        # prev_rev is self.previous_revision, unless it is a variant issue add
        from apps.oi.models import IssueRevision
        if self.added and type(self) is IssueRevision and self.variant_of:
            # for variant adds compare against base issue
            self._prev_rev = self.variant_of.revisions \
                                 .filter(committed=True,
                                         created__lt=self.created) \
                                 .latest('created')
        # edits which are not comitted do not have a stored previous revision
        elif self.committed is False and self.source:
            self._prev_rev = self.source.revisions \
                                 .filter(committed=True,
                                         created__lte=self.created) \
                                 .latest('created')
        return self._prev_rev

    def posterior(self):
        # This would be in the db cache anyway, but this way we
        # save db-calls in some cases.
        # During normal operation we cannot gain a new revision, so it's safe
        if hasattr(self, '_post_rev'):
            return self._post_rev

        self._post_rev = None
        if hasattr(self, 'next_revision'):
            self._post_rev = self.next_revision
        return self._post_rev

    def compare_changes(self, compare_revision=None):
        """
        Set up the 'changed' property so that it can be accessed conveniently
        from a template.  Template calling limitations prevent just
        using a parameter to compare one field at a time.
        """
        self.changed = {}
        self.is_changed = False

        if self.deleted:
            # deletion counts as changed to ease conditional for
            # collapsing sequences in bits/compare.html
            self.is_changed = True
            return

        # if we want to compare to some other revision, call with it
        if compare_revision:
            prev_rev = compare_revision
        else:
            prev_rev = self.previous()

        if prev_rev is None:
            self.is_changed = True
            prev_values = self._get_blank_values()
            get_prev_value = lambda field: prev_values[field]  # noqa: E731
        else:
            get_prev_value = lambda field: getattr(prev_rev,  # noqa: E731
                                                   field)
        for field_name in self.field_list():
            old = get_prev_value(field_name)
            new = getattr(self, field_name)
            if type(new) is str:
                field_changed = old.strip() != new.strip()
            elif isinstance(old, Manager):
                old = old.all().values_list('id', flat=True)
                new = new.all().values_list('id', flat=True)
                field_changed = set(old) != set(new)
            elif isinstance(new, Date):
                old = str(old)
                new = str(new)
                field_changed = old != new
            elif isinstance(new, Manager):
                new = new.all().values_list('id', flat=True)
                if new:
                    field_changed = True
                else:
                    field_changed = False
            else:
                field_changed = old != new
            self.changed[field_name] = field_changed
            self.is_changed |= field_changed
        from apps.oi.models import IssueRevision, StoryRevision
        if not self.is_changed and type(self) in [IssueRevision,
                                                  StoryRevision]:
            self.is_changed = self.has_reprint_revisions()

    def _start_imp_sum(self):
        """
        Hook for subclasses to initialize state for an IMP calculation.
        For instance, if a subclass is keeping track of whether either of a
        pair of fields that together represent an IMP have been seen, this
        hook can be used to clear that state before a new calculation begins.
        """
        pass

    def _imps_for(self, field_name):
        """
        Each revision subclass should override this and have it return the
        number of IMPs that a field should add to the total.  Note that this
        may be stateful as a change in one field may have already been
        accounted for due to a change in a related field.  Child classes may
        maintain state for this sort of tracking, and the _start_imp_sum hook
        should be overridden to clear any such state.
        """
        raise NotImplementedError

    def calculate_imps(self):
        """
        Calculate and return the number of Index Measurement Points that this
        revision is worth.  Relies on self.changed being set.
        """
        imps = 0
        self.compare_changes()
        if self.deleted or not self.is_changed:
            return imps

        other_imp = self._start_imp_sum()
        if other_imp:
            imps += other_imp
        for field_name in self.field_list():
            if field_name in self.changed and self.changed[field_name]:
                imps += self._imps_for(field_name)
        return imps

    def queue_name(self):
        """
        Long name form to display in queues.
        This allows revision objects to use their linked object's __str__
        method for compatibility in preview pages, but display a more
        verbose form in places like queues that need them.

        Derived classes should override _queue_name to supply a base string
        other than the standard unicode representation.
        """
        return self._queue_name()

    def _queue_name(self):
        return str(self)

    def queue_descriptor(self):
        """
        Display descriptor for queue name
        """
        if self.source is None:
            return '[ADDED]'
        if self.deleted:
            return '[DELETED]'
        return ''

    def save_added_revision(self, changeset, **kwargs):
        """
        Add the remaining arguments and many to many relations for an unsaved
        added revision produced by a model form.  The general workflow
        should be:

        revision = form.save(commit=False)
        revision.save_added_revision() # optionally with kwargs

        Since this prevents the form from adding any many to many
        relationships, the _do_save_added_revision method on each concrete
        revision class needs be certain to save any such relations that come
        from the form.
        """
        self.changeset = changeset
        self._do_complete_added_revision(**kwargs)
        self.save()

    def _do_complete_added_revision(self, **kwargs):
        """
        Hook for individual revisions to process additional parameters
        necessary to create a new revision representing an added record.
        By default no additional processing is done, so subclasses are
        free to override this method without calling it on the parent class.
        """
        pass

    def _create_dependent_revisions(self, delete=False, **kwargs):
        """
        Some Revisions have dependent objects, this locks the objects and
        creates the corresponding revisions.
        """
        if hasattr(self.source, 'external_link'):
            from apps.oi.models import ExternalLinkRevision
            for external_link in self.source.external_link.all():
                external_link_lock = _get_revision_lock(
                  external_link, changeset=self.changeset)
                if external_link_lock is None:
                    raise IntegrityError(
                      "needed External Link lock not possible")
                external_link_revision = ExternalLinkRevision.clone(
                    external_link, self.changeset, object_revision=self)
                if delete:
                    external_link_revision.deleted = self.deleted
                    external_link_revision.save()
        self._do_create_dependent_revisions(delete, **kwargs)

    def _create_external_link_formset(self, request):
        from apps.oi.forms import ExternalLinkRevisionFormSet

        return (ExternalLinkRevisionFormSet(
          request.POST or None,
          instance=self,
          queryset=self.external_link_revisions.filter(deleted=False)))

    def _process_external_link_formset(self, extra_forms):
        external_link_formset = extra_forms['external_link_formset']
        _process_formset(self, external_link_formset, generic=True)
        removed_external_links = external_link_formset.deleted_forms
        if removed_external_links:
            _removed_related_objects(removed_external_links, 'external_link')

    def _do_create_dependent_revisions(self, delete=False, **kwargs):
        """
        Some Revisions have dependent objects, this locks the objects and
        creates the corresponding revisions.
        """
        pass

    def has_keywords(self):
        return self.keywords != ''


class OngoingReservation(models.Model):
    """
    Represents the ongoing revision on all new issues in a series.

    Whenever an issue is added to a series, if there is an ongoing reservation
    for that series the issue is immediately reserved to the ongoing
    reservation holder.
    """
    class Meta:
        db_table = 'oi_ongoing_reservation'

    indexer = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='ongoing_reservations')
    series = models.OneToOneField(Series, on_delete=models.CASCADE,
                                  related_name='ongoing_reservation')
    along_with = models.ManyToManyField(User, related_name='ongoing_assisting')
    on_behalf_of = models.ManyToManyField(User, related_name='ongoing_source')

    """
    The creation timestamp for this reservation.
    """
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return '%s reserved by %s' % (self.series, self.indexer.indexer)


