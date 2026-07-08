"""Series add, series-bond, move and reorder views (roadmap C1). Shared changeset-workflow helpers come from apps.oi.views.core; re-exported through the package __init__ so the historical import surface is unchanged."""

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

from apps.oi.views.core import (  # noqa: F401
    REVISION_CLASSES, DISPLAY_CLASSES, REACHED_CHANGE_LIMIT, _cant_get,
    oi_render, delete, reserve, _do_reserve,
    edit_two_issues, confirm_two_edits, reserve_two_issues, reserve_other_issue,
    edit_revision, edit, _display_edit_form, submit,
    show_error_with_return, _save_data_source_revision, _extra_forms_valid, _save,
    retract, confirm_discard, discard, assign,
    release, discuss, _reserve_newly_created_issue, approve,
    _send_declined_reservation_email, _send_declined_ongoing_email, disapprove, send_comment_observer,
    add_comments, process, process_revision, add_generic,
    _process_reorder_form, _reorder_children)


@permission_required('indexer.can_reserve')
def add_series(request, publisher_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    # Process add form if this is a POST.
    try:
        publisher = Publisher.objects.get(id=publisher_id)
        if publisher.deleted or publisher.pending_deletion():
            return render_error(
              request, 'Cannot add series '
              'since "%s" is deleted or pending deletion.' % publisher)

        if request.method != 'POST':
            initial = {}
            initial['country'] = publisher.country.id
            # TODO: make these using same code as get_blank_values
            initial['has_barcode'] = True
            initial['has_isbn'] = True
            initial['is_comics_publication'] = True
            form = get_series_revision_form(publisher,
                                            user=request.user)(initial=initial)
            return _display_add_series_form(request, publisher, form)

        if 'cancel' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
              'show_publisher',
              kwargs={'publisher_id': publisher_id}))

        form = get_series_revision_form(publisher,
                                        user=request.user)(request.POST)
        if not form.is_valid():
            return _display_add_series_form(request, publisher, form)

        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['series'])
        changeset.save()
        revision = form.save(commit=False)
        revision.save_added_revision(changeset=changeset,
                                     publisher=publisher)
        return submit(request, changeset.id)

    except (Publisher.DoesNotExist, Publisher.MultipleObjectsReturned):
        return render_error(
          request, 'Could not find publisher for id ' + publisher_id)

def _display_add_series_form(request, publisher, form):
    kwargs = {
        'publisher_id': publisher.id,
    }
    url = urlresolvers.reverse('add_series', kwargs=kwargs)
    return oi_render(
      request, 'oi/edit/add_frame.html',
      {
        'object_name': 'Series',
        'object_url': url,
        'action_label': 'Submit New',
        'form': form,
      })

@permission_required('indexer.can_reserve')
def edit_series_bonds(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    return oi_render(request, 'oi/edit/list_series_bonds.html',
                     {'series': series, })

@permission_required('indexer.can_reserve')
def save_selected_series_bond(request, data, object_type, selected_id):
    if request.method != 'POST':
        return _cant_get(request)
    series_bond_revision = get_object_or_404(
      SeriesBondRevision, id=data['series_bond_revision_id'])
    if object_type == 'series':
        series = get_object_or_404(Series, id=selected_id)
        if data['which_side'] == 'origin':
            series_bond_revision.origin = series
            series_bond_revision.origin_issue = None
        else:
            series_bond_revision.target = series
            series_bond_revision.target_issue = None
    else:
        issue = get_object_or_404(Issue, id=selected_id)
        if data['which_side'] == 'origin':
            series_bond_revision.origin = issue.series
            series_bond_revision.origin_issue = issue
        else:
            series_bond_revision.target = issue.series
            series_bond_revision.target_issue = issue
    series_bond_revision.save()
    return HttpResponseRedirect(urlresolvers.reverse(
      'edit', kwargs={'id': series_bond_revision.changeset.id}))

@permission_required('indexer.can_reserve')
def edit_series_bond(request, id):
    if request.method != 'POST':
        return _cant_get(request)
    series_bond_revision = get_object_or_404(SeriesBondRevision, id=id)
    number = ''
    if 'edit_origin' in request.POST:
        which_side = 'origin'
        series = series_bond_revision.origin
        if series_bond_revision.origin_issue:
            number = series_bond_revision.origin_issue.number
    elif 'edit_target' in request.POST:
        which_side = 'target'
        series = series_bond_revision.target
        if series_bond_revision.target_issue:
            number = series_bond_revision.target_issue.number
    elif 'flip_direction' in request.POST:
        series = series_bond_revision.target
        issue = series_bond_revision.target_issue
        series_bond_revision.target = series_bond_revision.origin
        series_bond_revision.target_issue = series_bond_revision.origin_issue
        series_bond_revision.origin = series
        series_bond_revision.origin_issue = issue
        series_bond_revision.save()
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': series_bond_revision.changeset.id}))
    else:
        raise NotImplementedError
    initial = {'series': series.name,
               'publisher': series.publisher.name,
               'year': series.year_began,
               'number': number}
    data = {'series_bond_revision_id': id,
            'initial': initial,
            'series': True,
            'issue': True,
            'heading': mark_safe('<h2>Select %s of the bond %s</h2>' %
                                 (which_side, series_bond_revision)),
            'target': 'a series or issue',
            'return': 'save_selected_series_bond',
            'which_side': which_side,
            'cancel': urlresolvers.reverse('edit', kwargs={'id':
                                           series_bond_revision.changeset.id})}
    select_key = store_select_data(request, None, data)
    return HttpResponseRedirect(urlresolvers.reverse(
      'select_object', kwargs={'select_key': select_key}))

def save_added_series_bond(request, data, object_type, selected_id):
    if request.method != 'POST':
        return _cant_get(request)
    changeset = Changeset(indexer=request.user, state=states.OPEN,
                          change_type=CTYPES['series_bond'])
    changeset.save()
    series = get_object_or_404(Series, id=data['series_id'])
    if object_type == 'series':
        target = get_object_or_404(Series, id=selected_id)
        series_bond_revision = SeriesBondRevision(target=target)
    else:
        target_issue = get_object_or_404(Issue, id=selected_id)
        series_bond_revision = SeriesBondRevision(target=target_issue.series,
                                                  target_issue=target_issue)
    series_bond_revision.origin = series
    series_bond_revision.changeset = changeset
    series_bond_revision.save()
    return HttpResponseRedirect(urlresolvers.reverse(
      'edit', kwargs={'id': series_bond_revision.changeset.id}))

@permission_required('indexer.can_reserve')
def add_series_bond(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    data = {'series_id': series_id,
            'series': True,
            'issue': True,
            'heading': mark_safe('<h2>Select other side of the bond</h2>'),
            'target': 'a series or issue',
            'return': 'save_added_series_bond',
            'cancel': urlresolvers.reverse('show_series',
                                           kwargs={'series_id': series.id})}
    select_key = store_select_data(request, None, data)
    return HttpResponseRedirect(urlresolvers.reverse(
      'select_object', kwargs={'select_key': select_key}))

@permission_required('indexer.can_reserve')
def move_series(request, series_revision_id, publisher_id):
    series_revision = get_object_or_404(SeriesRevision, id=series_revision_id,
                                        deleted=False)
    if request.user != series_revision.changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may move series.')

    publisher = Publisher.objects.filter(id=publisher_id, deleted=False)
    if not publisher:
        return render_error(request, 'No publisher with id %s.'
                            % publisher_id, redirect=False)
    publisher = publisher[0]

    if request.method != 'POST':
        header_text = 'Do you want to move %s to <a href="%s">%s</a> ?' % \
          (esc(series_revision.series.full_name()),
           publisher.get_absolute_url(),
           esc(publisher))
        url = urlresolvers.reverse(
          'move_series',
          kwargs={'series_revision_id': series_revision_id,
                  'publisher_id': publisher_id})
        cancel_button = "Cancel"
        confirm_button = "move of series %s to publisher %s" % \
                         (series_revision.series, publisher)
        return oi_render(request, 'oi/edit/confirm.html',
                         {
                              'type': 'Series Move',
                              'header_text': mark_safe(header_text),
                              'url': url,
                              'cancel_button': cancel_button,
                              'confirm_button': confirm_button,
                         })
    else:
        if 'cancel' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit', kwargs={'id': series_revision.changeset.id}))
        else:
            if series_revision.changeset.issuerevisions.count() == 0:
                for issue in series_revision.series.active_issues():
                    if not _do_reserve(series_revision.changeset.indexer,
                                       issue, 'issue',
                                       changeset=series_revision.changeset):
                        for issue_rev in series_revision.changeset\
                                                        .issuerevisions.all():
                            _free_revision_lock(issue_rev.issue)
                            issue_rev.delete()
                        for story_rev in series_revision.changeset\
                                                        .storyrevisions.all():
                            _free_revision_lock(story_rev.story)
                            story_rev.delete()
                        return show_error_with_return(
                          request, 'Error while reserving issues.',
                          series_revision.changeset)
                for issue_revision in series_revision.changeset.issuerevisions\
                                                     .all():
                    for brand in issue_revision.brand_emblem.all():
                        new_brand = publisher.active_brand_emblems()\
                                             .filter(name=brand.name)
                        if new_brand.count() == 1:
                            issue_revision.brand_emblem.add(new_brand[0])
                        issue_revision.brand_emblem.remove(brand)
                    if issue_revision.indicia_publisher:
                        new_indicia_publisher = publisher\
                          .active_indicia_publishers()\
                          .filter(name=issue_revision.indicia_publisher.name)
                        if new_indicia_publisher.count() == 1:
                            issue_revision.indicia_publisher = \
                              new_indicia_publisher[0]
                        else:
                            issue_revision.indicia_publisher = None
                            issue_revision.no_indicia_publisher = False
                    issue_revision.save()
            series_revision.publisher = publisher
            series_revision.imprint = None
            series_revision.save()
            return submit(request, series_revision.changeset.id)

@permission_required('indexer.can_approve')
def reorder_series(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    if request.method != 'POST':
        return oi_render(
          request, 'oi/edit/reorder_series.html',
          {'series': series,
           'issue_list': [(i, None) for i in series.active_issues()]})

    try:
        issues = _process_reorder_form(request, series, 'sort_code',
                                       'issue', Issue)
        return _reorder_series(request, series, issues)
    except ViewTerminationError as vte:
        return vte.response

@permission_required('indexer.can_approve')
def reorder_series_by_key_date(request, series_id):
    if request.method != 'POST':
        return _cant_get(request)
    series = get_object_or_404(Series, id=series_id)

    issues = series.active_issues().order_by('key_date')
    return _reorder_series(request, series, issues)

@permission_required('indexer.can_approve')
def reorder_series_by_issue_number(request, series_id):
    if request.method != 'POST':
        return _cant_get(request)
    series = get_object_or_404(Series, id=series_id)

    reorder_map = {}
    reorder_list = []
    variant_counts = {}

    try:
        for issue in series.active_issues():
            number = int(issue.number)
            if number in reorder_list:
                if issue.variant_of:
                    if number in variant_counts:
                        variant_counts[number] += 1
                    else:
                        variant_counts[number] = 1
                    # there won't be more than 9999 variants...
                    number = float("%d.%04d" % (number,
                                                variant_counts[number]))
                else:
                    return render_error(
                      request,
                      "Cannot sort by issue with duplicate issue numbers: %i"
                      % number,
                      redirect=False)
            reorder_map[number] = issue
            reorder_list.append(number)

        reorder_list.sort()
        issues = [reorder_map[n] for n in reorder_list]
        return _reorder_series(request, series, issues)

    except ValueError:
        return render_error(
          request,
          "Cannot sort by issue numbers because they are not all whole "
          "numbers",
          redirect=False)

def _reorder_series(request, series, issues):
    """
    Internal method for actually changing the sort codes.
    Note that the 'issues' parameter may be either an ordered queryset
    or a plain list of issue objects.
    """

    # Note that _reorder_children actually performs the reordering, so it
    # is necessary even if we do not use the issue_list that it returns.
    # Do not move the call further down in this method.
    try:
        issue_list = _reorder_children(request, series, issues, 'sort_code',
                                       series.issue_set.all(),
                                       'commit' in request.POST,
                                       extras=series.issue_set.filter(
                                         deleted=True))
    except ViewTerminationError as vte:
        return vte.response

    if 'commit' in request.POST:
        set_series_first_last(series)
        return HttpResponseRedirect(urlresolvers.reverse(
          'show_series', kwargs={'series_id': series.id}))

    return oi_render(request, 'oi/edit/reorder_series.html',
                     {'series': series,
                      'issue_list': issue_list})
