"""Queue, compare, and preview views (roadmap C1). Shared changeset-workflow helpers come from apps.oi.views.core; re-exported through the package __init__ so the historical import surface is unchanged."""

import re
import sys
import glob
import PIL.Image as pyImage
from urllib.parse import unquote

from django.forms import HiddenInput, MultipleHiddenInput
import django.urls as urlresolvers
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction, IntegrityError
from django.db.models import Min, Max, Count, F, Q
from django.db.models.fields import Field
from django.utils.html import mark_safe, conditional_escape as esc

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType

from django_filters import FilterSet, MultipleChoiceFilter

from apps.stddata.models import Country

from apps.indexer.views import ViewTerminationError, render_error

from apps.gcd.models import (
    Brand, BrandGroup, BrandUse, Cover, Image, IndiciaPublisher, Issue,
    Publisher, Reprint, IssueCredit,
    Series, SeriesBond, Award, ReceivedAward, Creator,
    CreatorMembership, CreatorArtInfluence, CreatorDegree, CreatorNonComicWork,
    CreatorRelation, CreatorSchool, CreatorNameDetail,
    Story, StoryType, StoryArc, StoryArcRelation, STORY_TYPES, BiblioEntry,
    CharacterOrderType,
    Feature, FeatureLogo, FeatureRelation,
    Printer, IndiciaPrinter,
    CreatorSignature, Character, CharacterRelation, Group,
    GroupRelation, GroupMembership, Universe, CREDIT_TYPES)
from apps.gcd.views import paginate_response
# need this for preview-call
from apps.gcd.views.details import (  # noqa: F401
    show_publisher, show_indicia_publisher,
    show_brand_group, show_brand, show_series, show_issue, show_creator,
    show_creator_membership, show_received_award, show_creator_art_influence,
    show_creator_non_comic_work, show_creator_school, show_creator_degree,
    show_award, show_printer, show_indicia_printer, show_character,
    show_universe)

from apps.gcd.views.covers import get_image_tag, get_image_tags_per_issue
from apps.gcd.views.search import do_advanced_search, used_search
from apps.gcd.models.cover import ZOOM_LARGE, ZOOM_MEDIUM
from apps.oi.templatetags.editing import show_revision_short
from apps.select.views import store_select_data, get_cached_stories, \
                              get_cached_covers

from apps.oi.models import (
    Changeset, BrandGroupRevision, BrandRevision, BrandUseRevision,
    CoverRevision, ImageRevision, IndiciaPublisherRevision, IssueRevision,
    PublisherRevision, ReprintRevision, SeriesBondRevision, SeriesRevision,
    StoryRevision, BiblioEntryRevision, CharacterOrderRevision,
    OngoingReservation, RevisionLock,
    _get_revision_lock, _free_revision_lock, CTYPES,
    get_issue_field_list, set_series_first_last,
    AwardRevision, ReceivedAwardRevision, IssueCreditRevision,
    StoryCreditRevision, StoryCharacterRevision, StoryGroupRevision,
    StoryArcRevision, StoryArcRelationRevision, CreatorRevision,
    CreatorMembershipRevision,
    CreatorArtInfluenceRevision, CreatorNonComicWorkRevision,
    CreatorSchoolRevision, CreatorDegreeRevision, CreatorRelationRevision,
    FeatureRevision, FeatureLogoRevision, UniverseRevision,
    CharacterRevision, CharacterRelationRevision, GroupRevision,
    GroupRelationRevision, GroupMembershipRevision,
    PreviewBrand, PreviewIssue, PreviewStory, PreviewCharacter,
    PreviewReceivedAward, PreviewCreator, PreviewCreatorArtInfluence,
    PreviewCreatorDegree, PreviewCreatorMembership, PreviewCreatorNonComicWork,
    PreviewCreatorSchool, _get_creator_sourced_fields, on_sale_date_as_string,
    FeatureRelationRevision, process_data_source, PrinterRevision,
    IndiciaPrinterRevision, CreatorSignatureRevision, ChangesetComment,
    validated_isbn)

from apps.oi.forms import (get_brand_group_revision_form,  # noqa: F401
                           get_brand_revision_form,
                           get_brand_use_revision_form,
                           get_bulk_issue_revision_form,
                           get_award_revision_form,
                           get_received_award_revision_form,
                           get_creator_revision_form,
                           get_indicia_publisher_revision_form,
                           get_publisher_revision_form,
                           get_revision_form,
                           get_series_revision_form,
                           IssueRevisionFormSet,
                           ExternalLinkRevisionFormSet,
                           PublisherCodeNumberFormSet,
                           get_story_revision_form,
                           StoryRevisionFormSet,
                           StoryCharacterRevisionFormSet,
                           StoryGroupRevisionFormSet,
                           get_story_arc_relation_revision_form,
                           get_feature_logo_revision_form,
                           get_feature_relation_revision_form,
                           get_date_revision_form,
                           get_issue_revision_form_set_extra,
                           OngoingReservationForm,
                           CreatorRevisionFormSet,
                           CreatorArtInfluenceRevisionForm,
                           CreatorMembershipRevisionForm,
                           GroupMembershipRevisionForm,
                           CharacterRevisionFormSet,
                           GroupRevisionFormSet,
                           ReceivedAwardRevisionForm,
                           CreatorNonComicWorkRevisionForm,
                           CreatorRelationRevisionForm,
                           CreatorSchoolRevisionForm,
                           CreatorDegreeRevisionForm,
                           CreatorSignatureRevisionForm,
                           DateRevisionForm)
from apps.oi.forms.support import CREATOR_HELP_LINKS

from apps.oi.covers import get_preview_image_tag, \
                           get_preview_generic_image_tag, \
                           get_preview_image_tags_per_page, UPLOAD_WIDTH
from apps.oi import states
from apps.oi.templatetags.editing import is_locked

# core views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.core import (  # noqa: F401
    REVISION_CLASSES, DISPLAY_CLASSES, REACHED_CHANGE_LIMIT, _cant_get,
    oi_render, delete, reserve, _do_reserve,
    edit_two_issues, confirm_two_edits, reserve_two_issues, reserve_other_issue,
    edit_revision, edit, _display_edit_form, submit,
    show_error_with_return, _save_data_source_revision, _extra_forms_valid, _save,
    retract, confirm_discard, discard, assign,
    release, discuss, _reserve_newly_created_issue, approve,
    _send_declined_reservation_email, _send_declined_ongoing_email, disapprove, send_comment_observer,
    add_comments, process, process_revision,
    add_generic, _process_reorder_form, _reorder_children)


##############################################################################
# Queue Views
##############################################################################


def _revision_accessor(change_type):
    """
    The Changeset reverse accessor for a change type's revisions.

    Revisions relate to Changeset as '<lowercase-class-name>s', i.e. the
    change-type name without underscores plus 'revisions'. All the issue
    variants share the single IssueRevision set.
    """
    issue_family = ('issue', 'issue_add', 'issue_bulk',
                    'variant_add', 'two_issues')
    if change_type in issue_family:
        return 'issuerevisions'
    return change_type.replace('_', '') + 'revisions'


@permission_required('indexer.can_reserve')
def show_queue(request, queue_name):
    kwargs = {}
    if 'editing' == queue_name:
        kwargs['indexer'] = request.user
        kwargs['state__in'] = states.ACTIVE
    elif 'pending' == queue_name:
        kwargs['state__in'] = (states.PENDING, states.DISCUSSED,
                               states.REVIEWING)
    elif 'reviews' == queue_name:
        kwargs['approver'] = request.user
        kwargs['state__in'] = (states.OPEN, states.DISCUSSED,
                               states.REVIEWING)
    elif 'covers' == queue_name:
        return show_cover_queue(request)
    elif 'approved' == queue_name:
        return show_approved(request)
    elif 'commented' == queue_name:
        return show_commented(request)
    elif 'editor_log' == queue_name:
        return show_editor_log(request)

    changes = Changeset.objects.filter(**kwargs).select_related(
      'indexer__indexer', 'approver__indexer')

    def queue(change_type, *extra_prefetch):
        # Each queue row renders its revision and shows the change against the
        # previous revision, so always prefetch that; specialised buckets pass
        # extra source relations.
        accessor = _revision_accessor(change_type)
        return changes.filter(change_type=CTYPES[change_type]) \
                      .prefetch_related('%s__previous_revision' % accessor,
                                        *extra_prefetch)

    awards = queue('award')
    creators = queue('creator')
    creator_art_influences = queue('creator_art_influence')
    received_awards = queue('received_award')
    creator_memberships = queue('creator_membership')
    creator_non_comic_works = queue('creator_non_comic_work')
    creator_relations = queue('creator_relation')
    creator_schools = queue('creator_school')
    creator_signatures = queue('creator_signature')
    creator_degres = queue('creator_degree')
    publishers = queue('publisher', 'publisherrevisions__country')
    indicia_publishers = queue('indicia_publisher')
    brand_groups = queue('brand_group')
    brands = queue('brand')
    brand_uses = queue('brand_use')
    printers = queue('printer', 'printerrevisions__country')
    indicia_printers = queue('indicia_printer')
    series = queue('series', 'seriesrevisions__series')
    series_bonds = queue('series_bond')
    issue_adds = queue('issue_add', 'issuerevisions__issue',
                       'issuerevisions__series')
    issues = changes.filter(change_type__in=[CTYPES['issue'],
                                             CTYPES['variant_add'],
                                             CTYPES['two_issues']])\
                    .prefetch_related('issuerevisions__issue',
                                      'issuerevisions__variant_of',
                                      'issuerevisions__series',
                                      'issuerevisions__previous_revision')
    issue_bulks = queue('issue_bulk')
    covers = queue('cover', 'coverrevisions__cover')
    story_arcs = queue('story_arc')
    story_arc_relations = queue('story_arc_relation')
    features = queue('feature')
    feature_logos = queue('feature_logo')
    feature_relations = queue('feature_relation')
    universes = queue('universe')
    characters = queue('character')
    character_relations = queue('character_relation')
    groups = queue('group')
    group_relations = queue('group_relation')
    group_memberships = queue('group_membership')
    images = queue('image')
    countries = dict(Country.objects.values_list('id', 'code'))
    country_names = dict(Country.objects.values_list('id', 'name'))
    response = oi_render(
      request,
      'oi/queues/%s.html' % queue_name,
      {
        'queue_name': queue_name,
        'indexer': request.user,
        'states': states,
        'countries': countries,
        'country_names': country_names,
        'data': [
          {
            'object_name': 'Awards',
            'object_type': 'award',
            'changesets': awards.order_by('modified', 'id')
          },
          {
            'object_name': 'Creators',
            'object_type': 'creator',
            'changesets': creators.order_by('modified', 'id')
                                  .annotate(
              country=Max('creatorrevisions__birth_country__id'))
          },
          {
            'object_name': 'Creator Signatures',
            'object_type': 'creator_signature',
            'changesets': creator_signatures.order_by('modified', 'id')
                                            .annotate(
              country=Max(
                'creatorsignaturerevisions__creator__birth_country__id'))
          },
          {
            'object_name': 'Publishers',
            'object_type': 'publisher',
            'changesets': publishers.order_by('modified', 'id')
                                    .annotate(
              country=Max('publisherrevisions__country__id')),
          },
          {
            'object_name': 'Indicia / Colophon Publishers',
            'object_type': 'indicia_publisher',
            'changesets': indicia_publishers.order_by('modified', 'id')
                                            .annotate(
              country=Max('indiciapublisherrevisions__country__id')),
          },
          {
            'object_name': 'Brand Groups',
            'object_type': 'brand_groups',
            'changesets': brand_groups.order_by('modified', 'id')
                                      .annotate(
              country=Max('brandgrouprevisions__parent__country__id')),
          },
          {
            'object_name': 'Brand Emblems',
            'object_type': 'brands',
            'changesets': brands.order_by('modified', 'id')
                                .annotate(
              country=Max('brandrevisions__group__parent__country__id')),
          },
          {
            'object_name': 'Brand Uses',
            'object_type': 'brand_uses',
            'changesets': brand_uses.order_by('modified', 'id')
                                    .annotate(
              country=Max('branduserevisions__publisher__country__id')),
          },
          {
            'object_name': 'Printers',
            'object_type': 'printer',
            'changesets': printers.order_by('modified', 'id')
                                  .annotate(
              country=Max('printerrevisions__country__id')),
          },
          {
            'object_name': 'Indicia Printers',
            'object_type': 'indicia_printer',
            'changesets': indicia_printers.order_by('modified', 'id')
                                          .annotate(
              country=Max('indiciaprinterrevisions__country__id')),
          },
          {
            'object_name': 'Series',
            'object_type': 'series',
            'changesets': series.order_by('modified', 'id')
                                .annotate(country=Max(
                                          'seriesrevisions__country__id')),
          },
          {
            'object_name': 'Features',
            'object_type': 'feature',
            'changesets': features.order_by('modified', 'id')
          },
          {
            'object_name': 'Feature Logos',
            'object_type': 'feature_logo',
            'changesets': feature_logos.order_by('modified', 'id')
          },
          {
            'object_name': 'Story Arcs',
            'object_type': 'story_arc',
            'changesets': story_arcs.order_by('modified', 'id')
          },
          {
            'object_name': 'Universes',
            'object_type': 'universe',
            'changesets': universes.order_by('modified', 'id')
          },
          {
            'object_name': 'Characters',
            'object_type': 'character',
            'changesets': characters.order_by('modified', 'id')
          },
          {
            'object_name': 'Groups',
            'object_type': 'group',
            'changesets': groups.order_by('modified', 'id')
          },
          {
            'object_name': 'Issue Skeletons',
            'object_type': 'issue',
            'changesets': issue_adds.order_by('modified', 'id')
                                    .annotate(
              country=Max('issuerevisions__series__country__id')),
          },
          {
            'object_name': 'Issue Bulk Changes',
            'object_type': 'issue',
            'changesets': issue_bulks.order_by('state', 'modified', 'id')
                                     .annotate(
              country=Max('issuerevisions__series__country__id')),
          },
          {
            'object_name': 'Issues',
            'object_type': 'issue',
            'changesets': issues.order_by('state', 'modified', 'id')
                                .annotate(
              country=Max('issuerevisions__series__country__id')),
          },
          {
            'object_name': 'Received Awards',
            'object_type': 'received_award',
            'changesets': received_awards.order_by('modified', 'id')
          },
          {
            'object_name': 'Creator Art Influences',
            'object_type': 'creator_art_influence',
            'changesets': creator_art_influences.order_by('modified',
                                                          'id')
                                                .annotate(
              country=Max(
                'creatorartinfluencerevisions__creator__birth_country__id'))
          },
          {
            'object_name': 'Creator Degrees',
            'object_type': 'creator_degree',
            'changesets': creator_degres.order_by('modified', 'id')
                                        .annotate(
              country=Max(
                'creatordegreerevisions__creator__birth_country__id'))
          },
          {
            'object_name': 'Creator Memberships',
            'object_type': 'creator_membership',
            'changesets': creator_memberships.order_by('modified', 'id')
                                             .annotate(
              country=Max(
                'creatormembershiprevisions__creator__birth_country__id'))
          },
          {
            'object_name': 'Creator Non Comic Works',
            'object_type': 'creator_non_comic_work',
            'changesets': creator_non_comic_works.order_by('modified', 'id')
                                                 .annotate(
              country=Max(
                'creatornoncomicworkrevisions__creator__birth_country__id'))
          },
          {
            'object_name': 'Creator Relations',
            'object_type': 'creator_relation',
            'changesets': creator_relations.order_by('modified', 'id')
                                           .annotate(
              country=Max(
                'creatorrelationrevisions__from_creator__birth_country__id'))
          },
          {
            'object_name': 'Creator Schools',
            'object_type': 'creator_school',
            'changesets': creator_schools.order_by('modified', 'id')
                                         .annotate(
              country=Max(
                'creatorschoolrevisions__creator__birth_country__id'))
          },
          {
            'object_name': 'Series Bonds',
            'object_type': 'series_bond',
            'changesets': series_bonds.order_by('modified', 'id')
                                      .annotate(
              country=Max('seriesbondrevisions__origin__country__id')),
          },
          {
            'object_name': 'Feature Relations',
            'object_type': 'feature_relation',
            'changesets': feature_relations.order_by('modified', 'id')
          },
          {
            'object_name': 'Story Arc Relations',
            'object_type': 'story_arc_relation',
            'changesets': story_arc_relations.order_by('modified', 'id')
          },
          {
            'object_name': 'Character Relations',
            'object_type': 'character_relation',
            'changesets': character_relations.order_by('modified', 'id')
          },
          {
            'object_name': 'Group Relations',
            'object_type': 'group_relation',
            'changesets': group_relations.order_by('modified', 'id')
          },
          {
            'object_name': 'Group Memberships',
            'object_type': 'group_membership',
            'changesets': group_memberships.order_by('modified', 'id')
          },
          {
            'object_name': 'Covers',
            'object_type': 'cover',
            'changesets': covers.order_by('state', 'modified', 'id')
                                .annotate(
              country=Max('coverrevisions__issue__series__country__id')),
          },
          {
            'object_name': 'Images',
            'object_type': 'image',
            'changesets': images.order_by('state', 'modified', 'id'),
          },
        ],
      }
    )
    response['Cache-Control'] = "no-cache, no-store, max-age=0," \
                                " must-revalidate"
    return response


class ChangesetTypeFilter(FilterSet):
    choices = [[v, k] for k, v in CTYPES.items() if k not in ['unknown',]]
    change_type = MultipleChoiceFilter(choices=choices,
                                       label='Change Type')

    class Meta:
        model = Changeset
        fields = ['change_type',]


@login_required
def show_approved(request):

    changes = Changeset.objects.order_by('-modified')\
                       .filter(state=(states.APPROVED), indexer=request.user)

    filter = ChangesetTypeFilter(request.GET, changes)
    changes = filter.qs

    request_get = request.GET.copy()
    request_get.pop('page', None)
    request_get.pop('submit', None)
    query_string = request_get.urlencode()

    return paginate_response(
      request,
      changes,
      'oi/queues/approved.html',
      {'CTYPES': CTYPES, 'EDITING': True, 'queue_name': 'approved',
       'filter_form': filter.form,
       'query_string': query_string},
      per_page=50)


@login_required
def show_commented(request):
    commented = ChangesetComment.objects.exclude(text__in=['', 'Editing'])\
                                        .filter(changeset__migrated=False,
                                                commenter=request.user)

    deny = ChangesetComment.objects.exclude(text='')\
                                   .filter(changeset__indexer=request.user,
                                           commenter=F('changeset__approver'))

    comments = list(commented.values_list('id', flat=True)) + \
        list(deny.values_list('id', flat=True))

    changes = Changeset.objects.filter(comments__id__in=comments)\
                               .annotate(last_remark=Max('comments__created'))\
                               .distinct().order_by('-last_remark')\
                               .select_related('approver__indexer',
                                               'indexer__indexer')
    filter = ChangesetTypeFilter(request.GET, changes)
    changes = filter.qs

    request_get = request.GET.copy()
    request_get.pop('page', None)
    request_get.pop('submit', None)
    query_string = request_get.urlencode()

    return paginate_response(
      request,
      changes,
      'oi/queues/commented.html',
      {'CTYPES': CTYPES, 'EDITING': True, 'queue_name': 'commented',
       'filter_form': filter.form, 'query_string': query_string},
      per_page=50)


@login_required
def show_editor_log(request):
    changed_states = set(states.CLOSED+states.ACTIVE)
    changed_states.remove(states.REVIEWING)
    changes = Changeset.objects.order_by('-modified')\
                       .filter(comments__old_state=states.REVIEWING,
                               comments__new_state__in=changed_states,
                               comments__commenter=request.user)\
                       .exclude(indexer=request.user).distinct()
    filter = ChangesetTypeFilter(request.GET, changes)
    changes = filter.qs

    # TODO: check again with django 5
    request_get = request.GET.copy()
    request_get.pop('page', None)
    request_get.pop('submit', None)
    query_string = request_get.urlencode()

    return paginate_response(
      request,
      changes,
      'oi/queues/editor_log.html',
      {'CTYPES': CTYPES, 'EDITING': True, 'queue_name': 'editor_log',
       'filter_form': filter.form, 'query_string': query_string},
      per_page=50)


@login_required
def show_cover_queue(request):
    covers = Changeset.objects.filter(
      state__in=(states.PENDING, states.DISCUSSED, states.REVIEWING),
      change_type=CTYPES['cover']).select_related('indexer__indexer',
                                                  'approver__indexer')

    # TODO: Figure out optimal table width and/or make it user controllable.
    table_width = 5

    return paginate_response(
      request,
      covers,
      'oi/queues/covers.html',
      {'table_width': table_width, 'EDITING': True, 'queue_name': 'covers'},
      per_page=50,
      callback_key='tags',
      callback=get_preview_image_tags_per_page)


def compare(request, id):
    changeset = get_object_or_404(Changeset.objects
                                  .prefetch_related('comments__commenter'),
                                  id=id)

    if changeset.inline():
        revision = changeset.inline_revision()
    elif changeset.change_type in [CTYPES['issue'], CTYPES['issue_add'],
                                   CTYPES['issue_bulk'], CTYPES['variant_add'],
                                   CTYPES['two_issues']]:
        revision = changeset.issuerevisions.all()[0]
    elif changeset.change_type == CTYPES['series_bond']:
        revision = changeset.seriesbondrevisions.all()[0]
    else:
        # never reached at the moment
        raise NotImplementedError

    model_name = revision.source_name
    if model_name == 'cover':
        return cover_compare(request, changeset, revision)
    if model_name == 'image':
        return image_compare(request, changeset, revision)

    revision.compare_changes()

    if model_name == 'creator_signature':
        if changeset.imagerevisions.exists():
            return image_compare(request, changeset,
                                 changeset.imagerevisions.get(), revision)
    if model_name == 'feature_logo':
        if changeset.imagerevisions.exists():
            return image_compare(request, changeset,
                                 changeset.imagerevisions.get(), revision)
    if model_name == 'brand':
        if changeset.imagerevisions.exists():
            return image_compare(request, changeset,
                                 changeset.imagerevisions.get(), revision)
    if changeset.change_type == CTYPES['issue_add'] \
       and not (changeset.issuerevisions.count() == 1 and
                changeset.issuerevisions.get().variant_of is not None):
        template = 'oi/edit/compare_issue_skeletons.html'
    elif changeset.change_type == CTYPES['issue_bulk']:
        template = 'oi/edit/compare_bulk_issue.html'
    else:
        template = 'oi/edit/compare.html'

    prev_rev = revision.previous()
    post_rev = revision.posterior()
    field_list = revision.field_list()
    sourced_fields = None
    group_sourced_fields = None
    revisions_before = []
    revisions_after = []
    # eliminate fields that shouldn't appear in the compare
    if model_name == 'series':
        if not revision.imprint and \
          (prev_rev is None or prev_rev.imprint is None):
            field_list.remove('imprint')
        if not revision.format and (prev_rev is None
                                    or not prev_rev.format):
            field_list.remove('format')
        if not (revision.publication_notes or prev_rev and
                prev_rev.publication_notes):
            field_list.remove('publication_notes')
    elif model_name in ['indicia_publisher']:
        field_list.remove('parent')
    elif model_name == 'issue':
        if changeset.change_type == CTYPES['issue_bulk'] or \
          changeset.change_type == CTYPES['issue_add'] and \
          changeset.issuerevisions.count() > 1:
            field_list.remove('number')
            field_list.remove('notes')
            field_list.remove('year_on_sale')
            field_list.remove('month_on_sale')
            field_list.remove('day_on_sale')
            field_list.remove('on_sale_date_uncertain')
            if changeset.change_type == CTYPES['issue_bulk']:
                field_list.remove('title')
                field_list.remove('isbn')
                field_list.remove('barcode')
            else:
                field_list.remove('after')
                field_list.remove('publication_date')
                field_list.remove('key_date')
    elif changeset.change_type == CTYPES['creator']:
        sourced_fields = _get_creator_sourced_fields()
        sourced_fields['birth_date'] = 'birth_date'
        sourced_fields['death_date'] = 'death_date'
        group_sourced_fields = {'birth_city_uncertain': 'birth_place',
                                'death_city_uncertain': 'death_place'}
        creator_name_revisions = changeset.creatornamedetailrevisions.all()
        for creator_name_revision in creator_name_revisions:
            revisions_before.append(creator_name_revision)
    elif changeset.change_type == CTYPES['creator_membership']:
        sourced_fields = {'': 'membership_year_ended_uncertain'}
    elif changeset.change_type == CTYPES['received_award']:
        sourced_fields = {'': 'award_year_uncertain'}
    elif changeset.change_type in [CTYPES['creator_art_influence'],
                                   CTYPES['creator_degree'],
                                   CTYPES['creator_non_comic_work'],
                                   CTYPES['creator_relation'],
                                   CTYPES['creator_school'],
                                   CTYPES['creator_signature']]:
        sourced_fields = {'': 'notes'}
    elif changeset.change_type == CTYPES['character']:
        character_name_revisions = changeset.characternamedetailrevisions.all()
        for character_name_revision in character_name_revisions:
            revisions_before.append(character_name_revision)
    elif changeset.change_type == CTYPES['group']:
        group_name_revisions = changeset.groupnamedetailrevisions.all()
        for group_name_revision in group_name_revisions:
            revisions_before.append(group_name_revision)
    for revision_before in revisions_before:
        revision_before.compare_changes()
    for revision_after in revisions_after:
        revision_after.compare_changes()

    response = oi_render(request, template,
                         {'changeset': changeset,
                          'revision': revision,
                          'revisions_before': revisions_before,
                          'revisions_after': revisions_after,
                          'prev_rev': prev_rev,
                          'post_rev': post_rev,
                          'changeset_type': model_name.replace('_', ' '),
                          'model_name': model_name,
                          'states': states,
                          'field_list': field_list,
                          'sourced_fields': sourced_fields,
                          'group_sourced_fields': group_sourced_fields,
                          'source_fields': ['source_description',
                                            'source_type'],
                          'CTYPES': CTYPES},
                         )
    response['Cache-Control'] = "no-cache, no-store, max-age=0," \
                                " must-revalidate"
    return response


def get_cover_width(name):
    try:
        source_name = glob.glob(name)[0]
    except ValueError:
        if settings.BETA:
            return "'none given'"
        else:
            raise
    im = pyImage.open(source_name)
    cover_width = im.size[0]
    return cover_width


@login_required
def cover_compare(request, changeset, revision):
    '''
    Compare page for covers.
    - show uploaded cover
    - for replacement show former cover
    - for other active uploads show other existing and active covers
    '''
    if revision.deleted or revision.cover and revision.cover.deleted is True:
        cover_tag = get_image_tag(revision.cover, "deleted cover", ZOOM_LARGE)
    else:
        cover_tag = get_preview_image_tag(revision, "uploaded cover",
                                          ZOOM_LARGE, request=request)
    kwargs = {'changeset': changeset,
              'revision': revision,
              'cover_tag': cover_tag,
              'table_width': 5,
              'states': states,
              'settings': settings}
    if revision.is_wraparound:
        kwargs['cover_front_tag'] = get_preview_image_tag(
          revision, "uploaded cover", ZOOM_MEDIUM, request=request)
    if revision.is_replacement:
        # change this to use cover.previous() once we are using
        # cover.reserved = True for cover replacements and
        # cleared out cover uploads from editing limbo
        # possible problem scenario:
        # replacement a) is retracted/sent back
        # replacement b) is submitted and approved
        # replacement a) is submitted and approved
        # then the order would be wrong
        old_cover = CoverRevision.objects.filter(
          cover=revision.cover,
          created__lt=revision.created,
          changeset__change_type=CTYPES['cover'],
          changeset__state=states.APPROVED).order_by('-created')[0]
        kwargs['old_cover'] = old_cover
        kwargs['old_cover_tag'] = get_preview_image_tag(
          old_cover, "replaced cover", ZOOM_LARGE, request=request)
        if old_cover.is_wraparound:
            kwargs['old_cover_front_tag'] = get_preview_image_tag(
              old_cover, "replaced cover", ZOOM_MEDIUM, request=request)

        if old_cover.created <= settings.NEW_SITE_COVER_CREATION_DATE:
            # uploaded file too old, not stored, we have width 400
            kwargs['old_cover_width'] = 400
        else:
            kwargs['old_cover_width'] = get_cover_width("%s/uploads/%d_%s*" % (
              old_cover.cover.base_dir(),
              old_cover.cover.id,
              old_cover.changeset.created.strftime('%Y%m%d_%H%M%S')))

    if revision.deleted:
        kwargs['old_cover'] = CoverRevision.objects.filter(
          cover=revision.cover, created__lt=revision.created,
          changeset__state=states.APPROVED).order_by('-created')[0]

    if revision.changeset.state in states.ACTIVE:
        if revision.issue.has_covers() or revision.issue.variant_covers() or \
          (revision.issue.variant_of and
           revision.issue.variant_of.has_covers()):
            # no issuerevision, so no variant upload,
            # but covers exist for issue
            if revision.issue.has_covers() and not \
              revision.changeset.issuerevisions.count():
                kwargs['additional'] = True
            current_covers = []
            current_cover_set = revision.issue.active_covers() | \
                revision.issue.variant_covers()
            if revision.is_replacement or revision.deleted:
                current_cover_set = current_cover_set.exclude(
                  id=revision.cover.id)
            for cover in current_cover_set:
                current_covers.append([cover, get_image_tag(cover,
                                       "current cover", ZOOM_MEDIUM)])
            kwargs['current_covers'] = current_covers
        cover_revisions = CoverRevision.objects.filter(
          issue=revision.issue) | CoverRevision.objects.filter(
          issue=revision.issue.variant_of) | CoverRevision.objects.filter(
          issue__in=revision.issue.variant_set.all())
        cover_revisions = cover_revisions.exclude(
          id=revision.id).filter(cover=None)\
                         .filter(changeset__state__in=states.ACTIVE) \
                         .order_by('created')
        if len(cover_revisions):
            pending_covers = []
            for cover in cover_revisions:
                pending_covers.append([cover, get_preview_image_tag(cover,
                                       "pending cover", ZOOM_MEDIUM)])
            kwargs['pending_covers'] = pending_covers
        kwargs['pending_variant_adds'] = Changeset.objects.filter(
          issuerevisions__variant_of=revision.issue,
          state__in=[states.PENDING, states.REVIEWING],
          change_type__in=[CTYPES['issue_add'],
                           CTYPES['variant_add']])
        # TODO This doesn't include the case of a variant with a
        # deleted cover scan.
        kwargs['variants_without_covers'] = revision.issue.variant_set\
                                                    .filter(cover=None)

        if revision.deleted is False:
            kwargs['cover_width'] = get_cover_width(revision.base_dir() +
                                                    str(revision.id) + '*')
    else:
        if revision.created <= settings.NEW_SITE_COVER_CREATION_DATE:
            # uploaded file too old, not stored, we have width 400
            kwargs['cover_width'] = 400
        elif revision.deleted is False:
            if revision.changeset.state == states.DISCARDED:
                kwargs['cover_width'] = get_cover_width(revision.base_dir() +
                                                        str(revision.id) + '*')
            else:
                kwargs['cover_width'] = get_cover_width("%s/uploads/%d_%s*" % (
                  revision.cover.base_dir(),
                  revision.cover.id,
                  revision.changeset.created.strftime('%Y%m%d_%H%M%S')))

    response = oi_render(request, 'oi/edit/compare_cover.html', kwargs)
    response['Cache-Control'] = "no-cache, no-store, max-age=0," \
                                " must-revalidate"
    return response


def image_compare(request, changeset, revision, extra_revision=None):
    '''
    Compare page for images.
    - show uploaded image
    - for replacement show former image
    '''
    # for non-portraits, request.user should be authenticated
    # for portraits we always show the changeset for source and attribution
    if not request.user.is_authenticated and revision.type.id != 4:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    image_tag = get_preview_generic_image_tag(revision, "uploaded image")
    kwargs = {'changeset': changeset,
              'revision': revision,
              'extra_revision': extra_revision,
              'image_tag': image_tag,
              'states': states,
              'settings': settings}
    if extra_revision:
        kwargs['prev_rev'] = extra_revision.previous()
        kwargs['post_rev'] = extra_revision.posterior()
        kwargs['field_list'] = extra_revision.field_list()
        if changeset.change_type == CTYPES['creator_signature']:
            sourced_fields = {'': 'notes'}
            kwargs['sourced_fields'] = sourced_fields
            kwargs['source_fields'] = ['source_description', 'source_type']

    if changeset.state != states.APPROVED and revision.type.unique \
       and not extra_revision:
        if Image.objects.filter(
          content_type=ContentType.objects.get_for_model(revision.object),
          object_id=revision.object.id, type=revision.type, deleted=False)\
          .count():
            kwargs['double_upload'] = '%s has an %s. Additional images ' \
              'cannot be uploaded, only replacements are possible.' \
              % (revision.object, revision.type.description)

    if revision.is_replacement:
        replaced_image = revision.previous()
        kwargs['replaced_image'] = replaced_image
        kwargs['replaced_image_tag'] = get_preview_generic_image_tag(
                                        replaced_image, "replaced image")
        if changeset.state != states.APPROVED:
            kwargs['replaced_image_marked'] = revision.image.marked
            kwargs['replaced_image_file'] = revision.image.image_file
        else:
            kwargs['replaced_image_file'] = replaced_image.image_file

    response = oi_render(request, 'oi/edit/compare_image.html', kwargs)
    response['Cache-Control'] = "no-cache, no-store, max-age=0," \
                                " must-revalidate"
    return response


@login_required
def preview(request, id, model_name):
    revision = get_object_or_404(REVISION_CLASSES[model_name], id=id)

    if model_name in ['publisher', 'indicia_publisher', 'brand_group',
                      'brand', 'printer', 'indicia_printer', 'series',
                      'issue', 'award', 'creator', 'character',
                      'universe',
                      'received_award', 'creator_art_influence',
                      'creator_degree', 'creator_membership',
                      'creator_non_comic_work', 'creator_school']:
        # TODO the model specific settings very likely should be methods
        #      on the revision
        if model_name == 'brand':
            # fake for brand emblems the group_set
            if revision.source:
                model_object = PreviewBrand(revision.source)
                for field in revision._get_irregular_fields():
                    setattr(model_object, field,
                            getattr(revision.source, field))
            else:
                model_object = PreviewBrand()
            model_object._group = revision.group
        elif model_name == 'issue':
            # TODO add and use PreviewIssue.init
            if revision.source:
                model_object = PreviewIssue(revision.source)
                model_object.sort_code = revision.source.sort_code
            else:
                model_object = PreviewIssue()
                model_object.after = revision.after
            model_object.issuerevisions = revision.changeset.issuerevisions
            model_object.storyrevisions = revision.changeset.storyrevisions
            model_object.series = revision.series
            model_object.revision = revision
            model_object.on_sale_date = on_sale_date_as_string(revision)
            model_object.valid_isbn = validated_isbn(revision.isbn)
            # on preview show all story types
            request.GET = request.GET.copy()
            request.GET['issue_detail'] = 2
        elif model_name == 'character':
            model_object = PreviewCharacter()
            model_object.revision = revision
        elif model_name == 'creator':
            model_object = PreviewCreator()
            model_object.revision = revision
        elif model_name == 'received_award':
            model_object = PreviewReceivedAward()
            model_object.revision = revision
        elif model_name == 'creator_art_influence':
            model_object = PreviewCreatorArtInfluence()
            model_object.revision = revision
        elif model_name == 'creator_degree':
            model_object = PreviewCreatorDegree()
            model_object.revision = revision
        elif model_name == 'creator_membership':
            model_object = PreviewCreatorMembership()
            model_object.revision = revision
        elif model_name == 'creator_non_comic_work':
            model_object = PreviewCreatorNonComicWork()
            model_object.revision = revision
        elif model_name == 'creator_school':
            model_object = PreviewCreatorSchool()
            model_object.revision = revision
        else:
            if revision.source:
                model_object = revision.source
            else:
                model_object = revision.source_class()
        if not revision.source:
            # this of course depends on there being no valid data with id 0
            model_object.id = 0
        else:
            model_object.id = revision.source.id
        revision._copy_fields_to(model_object)
        # keywords are a TextField for the revision, but a M2M-relation
        # for the model, overwrite for preview.
        # TODO should all have keywords ?
        if model_name not in ['award', 'creator', 'received_award',
                              'creator_art_influence', 'creator_degree',
                              'creator_membership', 'creator_non_comic_work',
                              'creator_school', 'universe']:
            model_object.keywords = revision.keywords
            if revision.keywords:
                model_object.has_keywords = True
            else:
                model_object.has_keywords = False
        return globals()['show_%s' % (model_name)](request, model_object, True)
    return render_error(request,
                        'No preview for "%s" revisions.' % model_name)

