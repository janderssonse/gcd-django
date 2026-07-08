# -*- coding: utf-8 -*-


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

# publisher views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.publisher import (  # noqa: F401
    add_publisher, add_indicia_publisher, add_brand_group, add_brand,
    _display_add_brand_form, add_brand_use, process_add_brand_use, _display_add_brand_use_form,
    add_printer, add_indicia_printer)

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
# Bulk Changes
##############################################################################


def _clean_bulk_issue_change_form(form, remove_fields, items,
                                  number_of_issues=True):
    for i in remove_fields:
        form.fields.get(i).widget = HiddenInput()
        if i in ['brand_emblem', 'indicia_printer']:
            form.fields.get(i).widget = MultipleHiddenInput()
    return form


@permission_required('indexer.can_reserve')
def edit_issues_in_bulk(request):
    """
    Handles the bulk editing of multiple issues found via advanced search.

    This view allows an indexer to apply the same change to multiple issues
    at once. The process is as follows:
    1.  The view is initiated from an advanced search result for issues.
    2.  It fetches all issues matching the search criteria.
    3.  It checks which of these issues are not currently reserved (locked) by
        other users. If all are reserved, an error is shown.
    4.  It analyzes the fields of the unreserved issues. A field is only
        made available for editing if all selected issues share the exact same
        initial value for that field. Fields with differing values across the
        set of issues are not displayed on the form. Certain fields that are
        inherently unique per issue (e.g., 'number', 'isbn', 'key_date') are
        always excluded from bulk editing.
    5.  A similar analysis is performed for credits.
        If all issues have an identical set of credits, a formset is provided
        to edit them. Otherwise, credit editing is disabled.
    6.  On a GET request, it displays a form containing only the editable
        fields, pre-populated with their common values.
    7.  On a POST request, it validates the submitted form data. If valid, it
        creates a new Changeset, reserves each unreserved issue and generates
        an IssueRevision, applying the submitted changes. It also handles the
        creation and modification of credit revisions if applicable.

    Returns:
        HttpResponse:
        - Renders the bulk edit form on a GET request.
        - Redirects to the advanced search page if the request is invalid,
          canceled, or if no issues can be edited.
        - Renders an error page if a critical error occurs (e.g., user has
          reached their change limit, all issues are reserved).
        - Redirects to the submit page upon successful creation of the
          bulk change revisions.
    """
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    if request.method == 'GET' and request.GET['target'] != 'issue':
        return HttpResponseRedirect(urlresolvers.reverse(
          'process_advanced_search') + '?' + request.GET.urlencode())

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'process_advanced_search') + '?' + request.GET.urlencode())

    search_values = request.GET.copy()
    target, method, logic, used_search_terms = used_search(search_values)

    try:
        items, target_name = do_advanced_search(request)
    except ViewTerminationError:
        return render_error(
          request,
          'The search underlying the bulk change was not successful. '
          'This should not happen. Please try again. If this error message '
          'persists, please contact an Editor.')

    ids = list(items.values_list('id', flat=True))
    items = Issue.objects.filter(id__in=ids)
    nr_items = items.count()
    items_reserved = RevisionLock.objects.filter(
      object_id__in=ids,
      content_type=ContentType.objects.get_for_model(items[0]))
    nr_items_reserved = items_reserved.count()
    nr_items_unreserved = nr_items - nr_items_reserved
    items_reserved_ids = items_reserved.values_list('object_id', flat=True)
    items_reserved = Issue.objects.filter(id__in=items_reserved_ids)
    if nr_items_unreserved == 0:
        if nr_items == 0:  # shouldn't really happen
            return HttpResponseRedirect(urlresolvers.reverse(
              'process_advanced_search') + '?' + request.GET.urlencode())
        else:
            return render_error(
              request,
              'All issues fulfilling the search criteria for the bulk change'
              ' are currently reserved.')

    remove_fields = []  # field to take out of the form

    series_list = list(set(items.values_list('series', flat=True)))
    ignore_publisher = False
    if len(series_list) == 1:
        series = Series.objects.get(id=series_list[0])
        series_list = []
    else:
        if len(items) > 100:  # shouldn't happen, just in case
            raise ValueError(
              'not more than 100 issues if more than one series')
        publisher_list = Publisher.objects.exclude(deleted=True) \
                                  .filter(series__in=series_list).distinct()
        series_list = Series.objects.exclude(deleted=True)\
                                    .filter(id__in=series_list)
        series = series_list[0]
        if len(publisher_list) > 1:
            ignore_publisher = True

    if not series.has_barcode or \
       any(series.has_barcode != s.has_barcode for s in series_list):
        remove_fields.append('no_barcode')
    if not series.has_indicia_frequency or \
       any(series.has_indicia_frequency != s.has_indicia_frequency
            for s in series_list):
        remove_fields.append('no_indicia_frequency')
        remove_fields.append('indicia_frequency')
    if not series.has_indicia_printer or \
       any(series.has_indicia_printer != s.has_indicia_printer
           for s in series_list):
        remove_fields.append('indicia_printer_not_printed')
        remove_fields.append('indicia_printer')
        remove_fields.append('indicia_printer_sourced_by')
    if not series.has_isbn or \
       any(series.has_isbn != s.has_isbn for s in series_list):
        remove_fields.append('no_isbn')
    if not series.has_issue_title or \
       any(series.has_issue_title != s.has_issue_title for s in series_list):
        remove_fields.append('no_title')
    if not series.has_rating or \
       any(series.has_rating != s.has_rating for s in series_list):
        remove_fields.append('no_rating')
        remove_fields.append('rating')
    if not series.has_volume or \
       any(series.has_volume != s.has_volume for s in series_list):
        remove_fields.append('no_volume')
        remove_fields.append('volume')
        remove_fields.append('volume_not_printed')
        remove_fields.append('display_volume_with_number')

    form_class = get_bulk_issue_revision_form(series, 'bulk_edit',
                                              user=request.user)

    fields = get_issue_field_list()
    fields.remove('number')
    fields.remove('year_on_sale')
    fields.remove('month_on_sale')
    fields.remove('day_on_sale')
    fields.remove('on_sale_date_uncertain')
    fields.remove('isbn')
    fields.remove('notes')
    fields.remove('barcode')
    fields.remove('title')
    fields.remove('keywords')
    # look at values for the issue fields
    # if only one it gives the initial value
    # if several, the field is not editable
    initial = {}  # init value is the common value for all issues
    empty_not_allowed = ['publication_date', 'key_date', ]

    # there are several publishers, ignore publisher related fields
    if ignore_publisher:
        remove_fields.append('brand_emblem')
        remove_fields.append('no_brand')
        remove_fields.append('indicia_publisher')
        remove_fields.append('indicia_pub_not_printed')

    for i in fields:
        if i not in remove_fields:
            values_list = list(set(items.values_list(i, flat=True)))
            if len(values_list) > 1 or (len(values_list) == 1 and
                                        i in empty_not_allowed and
                                        values_list[0] in [None, '']):
                remove_fields.append(i)
                # some fields belong together, both are either in or out
                if i in ['volume', 'brand', 'editing', 'indicia_frequency',
                         'rating']:
                    if 'no_' + i not in remove_fields:
                        remove_fields.append('no_' + i)
                elif i in ['no_volume', 'no_editing',
                           'no_indicia_frequency', 'no_rating']:
                    if i[3:] not in remove_fields:
                        remove_fields.append(i[3:])
                elif i == 'no_brand':
                    if 'brand_emblem' not in remove_fields:
                        remove_fields.append('brand_emblem')
                elif i == 'brand_emblem':
                    if 'no_brand' not in remove_fields:
                        remove_fields.append('no_brand')
                elif i == 'indicia_publisher':
                    remove_fields.append('indicia_pub_not_printed')
                elif i == 'indicia_pub_not_printed':
                    remove_fields.append('indicia_publisher')
                elif i == 'indicia_printer':
                    remove_fields.append('indicia_printer_not_printed')
                elif i == 'indicia_printer_not_printed':
                    remove_fields.append('indicia_printer')
                elif i == 'page_count':
                    remove_fields.append('page_count_uncertain')
                elif i == 'page_count_uncertain':
                    remove_fields.append('page_count')
                elif i == 'publication_date':
                    remove_fields.append('key_date')
                elif i == 'key_date':
                    remove_fields.append('publication_date')

    for i in ['no_barcode', 'no_isbn']:
        if i not in remove_fields:
            values_list = list(set(items.values_list(i[3:], flat=True)))
            if len(values_list) > 1:
                remove_fields.append(i)

    # creator_id is first field in processing, exclude and add back later
    excluded_names = ['id', 'issue_id', 'deleted', 'modified', 'created',
                      'creator_id']
    data_fields = {
        f.get_attname(): f
        for f in IssueCredit._meta.get_fields()
        if isinstance(f, Field) and f.get_attname() not in excluded_names
    }
    editing_credits = items.filter(credits__deleted=False).exists()
    if editing_credits and 'editing' not in remove_fields and 'no_editing' \
       not in remove_fields:
        reference_issue = items[0]
        editing_credits = reference_issue.credits.filter(deleted=False)
        issue_count = 1
        for issue in items[1:]:
            if issue.credits.filter(deleted=False).count() == editing_credits\
                                                              .count():
                count = 0
                for credit in issue.credits.filter(deleted=False):
                    query = Q(**{'%s' % ('creator_id'): getattr(credit,
                                                                'creator_id')})
                    for field in data_fields:
                        query &= Q(**{'%s' % (field): getattr(credit, field)})
                    if editing_credits.filter(query).exists():
                        count += 1
                    else:
                        break
                if count != editing_credits.count():
                    break
                else:
                    issue_count += 1
            else:
                break
        if issue_count == len(items):
            if request.method != 'POST':
                credits_formset = get_issue_revision_form_set_extra(
                    extra=editing_credits.count()+1)(
                      initial=editing_credits.values(
                              *editing_credits[0].revisions.first()
                                                 ._field_list()))
            else:
                credits_formset = IssueRevisionFormSet(request.POST or None)
        else:
            credits_formset = None
            if 'no_editing' not in remove_fields:
                remove_fields.append('no_editing')
    elif 'editing' not in remove_fields and 'no_editing' not in remove_fields:
        credits_formset = IssueRevisionFormSet(request.POST or None)
    else:
        credits_formset = None
    data_fields = list(data_fields)
    data_fields.append('creator_id')

    for i in fields:
        if i not in remove_fields:
            values_list = list(set(items.values_list(i, flat=True)))
            initial[i] = values_list[0]

    if request.method != 'POST':
        form = _clean_bulk_issue_change_form(form_class(initial=initial),
                                             remove_fields, items)
        return _display_bulk_issue_change_form(
          request, form, credits_formset, nr_items, nr_items_unreserved,
          items_reserved,
          request.GET.urlencode(), target, method, logic, used_search_terms)

    form = form_class(request.POST)
    if not form.is_valid() or (credits_formset and
                               not credits_formset.is_valid()):
        form = _clean_bulk_issue_change_form(form, remove_fields, items,
                                             number_of_issues=False)
        return _display_bulk_issue_change_form(
          request, form, credits_formset, nr_items, nr_items_unreserved,
          items_reserved,
          request.GET.urlencode(), target, method, logic, used_search_terms)

    changeset = Changeset(indexer=request.user, state=states.OPEN,
                          change_type=CTYPES['issue_bulk'])
    changeset.save()
    comment = 'Used search terms:\n'
    for search in used_search_terms:
        comment += '%s : %s\n' % (search[0], search[1])
    comment += 'method : %s\n' % method
    comment += 'behavior : %s\n' % logic
    # cannot use urlencode since urlize needs plain text
    # and urlencode would encode non-ASCII characters
    query_string = ''
    for entry in request.GET.items():
        if query_string == '':
            query_string += '?%s=%s' % entry
        else:
            query_string += '&%s=%s' % entry
    comment += 'Search results: %s%s%s' % (
      settings.SITE_URL.rstrip('/'),
      urlresolvers.reverse('process_advanced_search'),
      query_string.replace(' ', '+'))

    changeset.comments.create(commenter=request.user,
                              text=comment,
                              old_state=changeset.state,
                              new_state=changeset.state)

    cd = form.cleaned_data
    if credits_formset:
        cd_credits = []
        for form in credits_formset:
            if form.is_valid():
                cd_credits.append(form.cleaned_data)
    for issue in items:
        revision_lock = _get_revision_lock(issue, changeset)
        if revision_lock:
            revision = IssueRevision.clone(issue, changeset=changeset)
            for field in initial:
                if field in ['brand', 'indicia_publisher'] and \
                   cd[field] is not None:
                    setattr(revision, field + '_id', cd[field].id)
                elif field in ['brand_emblem', 'indicia_printer'] and \
                        cd[field] is not None:
                    getattr(revision, field).set(cd[field].all())
                else:
                    setattr(revision, field, cd[field])
            revision.save()

            if credits_formset:
                existing_credits = issue.credits.filter(deleted=False)
                for cd_credit in cd_credits:
                    if existing_credits.filter(
                       creator__creator__id=cd_credit['creator'].creator_id)\
                       .exists():
                        credit = existing_credits.filter(
                          creator__creator__id=cd_credit['creator'].creator_id
                          ).first()
                        revision_lock = _get_revision_lock(credit, changeset)
                        if not revision_lock:
                            raise ValueError('could not lock credit')
                        credit_revision = IssueCreditRevision.clone(
                          credit, issue_revision=revision, changeset=changeset)
                    else:
                        credit_revision = IssueCreditRevision(
                          issue_revision=revision, changeset=changeset,
                          creator=cd_credit['creator'],
                          credit_type=cd_credit['credit_type'])
                    for field in data_fields:
                        if field in ['creator_id', 'credit_type_id']:
                            setattr(credit_revision, field,
                                    cd_credit[field[:-3]].id)
                        else:
                            setattr(credit_revision, field, cd_credit[field])
                    credit_revision.save()
                for credit in issue.active_credits:
                    if not is_locked(credit):
                        revision_lock = _get_revision_lock(credit, changeset)
                        if not revision_lock:
                            raise ValueError('could not lock credit')
                        credit_revision = IssueCreditRevision.clone(
                          credit, issue_revision=revision, changeset=changeset)
                        credit_revision.deleted = True
                        credit_revision.save()
    # safety check, did happen that issues got reserved in-between
    if not changeset.issuerevisions.exists():
        return render_error(
          request,
          'All issues fulfilling the search criteria for the bulk change'
          ' are currently reserved.')

    return submit(request, changeset.id)


def _display_bulk_issue_change_form(request, form, credits_formset,
                                    nr_items, nr_items_unreserved,
                                    items_reserved,
                                    search_option,
                                    target, method, logic, used_search_terms):
    url_name = 'edit_issues_in_bulk'
    url = urlresolvers.reverse(url_name) + '?' + search_option
    return oi_render(
      request, 'oi/edit/bulk_frame.html',
      {
        'object_name': 'Issues',
        'object_url': url,
        'action_label': 'Submit bulk change',
        'form': form,
        'credits_formset': credits_formset,
        'nr_items': nr_items,
        'nr_items_unreserved': nr_items_unreserved,
        'items_reserved': items_reserved,
        'target': target,
        'method': method,
        'logic': logic,
        'used_search_terms': used_search_terms,
      })

##############################################################################
# Adding Items
##############################################################################






















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


def init_added_variant(form_class, initial, issue, revision=False):
    for key in list(initial):
        if key.startswith('_'):
            initial.pop(key)
    if issue.brand_emblem:
        initial['brand_emblem'] = issue.brand_emblem.all()
    if issue.indicia_printer:
        initial['indicia_printer'] = issue.indicia_printer.all()
    if issue.indicia_publisher:
        initial['indicia_publisher'] = issue.indicia_publisher.id
    initial['variant_name'] = ''
    if revision:
        issue = issue.issue
    if issue.variant_set.filter(deleted=False).count():
        initial['after'] = issue.variant_set.filter(deleted=False)\
                                            .latest('sort_code').id
    form = form_class(initial=initial)
    return form


@permission_required('indexer.can_reserve')
def add_issue(request, series_id, sort_after=None, variant_of=None,
              variant_cover=None, edit_with_base=False):
    """
    Add a new issue to a series with optional variant handling.
    This view handles the creation of new issues, including base issues and
    variant issues. It manages the complete workflow from form display through
    validation to changeset creation.

    Args:
        series_id: The ID of the series to which the issue will be added
        sort_after: Optional; issue after which this issue should be sorted
        variant_of: Optional; base issue if this is a variant issue
        variant_cover: Optional; cover associated with the variant
        edit_with_base: Boolean flag indicating if editing alongside base issue

    Returns:
        HttpResponse: On GET requests or invalid forms, displays the issue
                        addition form. On successful POST with variant_of and
                        edit_with_base, redirects to reserve the base issue or
                        cover. On successful POST for base issues, redirects to
                        either issue comparison (if copying from predecessor)
                        or submission. Returns error page if user has reached
                        change limit or series is deleted.

    Raises:
        Http404: If the series with the given series_id does not exist.

    Notes:
        - Checks if user can reserve another change before proceeding.
        - Handles cancellation by redirecting to appropriate pages.
        - Validates series is not deleted or pending deletion.
        - Creates formsets for credits, publisher codes, and external links.
        - For variants, initializes form with base issue data.
        - Creates changeset and issue revision on successful form submission.
    """

    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    if 'cancel' in request.POST:
        if variant_of:
            return HttpResponseRedirect(urlresolvers.reverse(
              'show_issue',
              kwargs={'issue_id': variant_of.id}))
        else:
            return HttpResponseRedirect(urlresolvers.reverse(
              'show_series',
              kwargs={'series_id': series_id}))

    series = get_object_or_404(Series, id=series_id)
    if series.deleted or series.pending_deletion():
        return render_error(
          request, 'Cannot add an issue '
          'since "%s" is deleted or pending deletion.' % series)

    form_class = get_revision_form(model_name='issue',
                                   series=series,
                                   publisher=series.publisher,
                                   variant_of=variant_of,
                                   user=request.user,
                                   edit_with_base=edit_with_base)
    credits_formset = IssueRevisionFormSet(request.POST or None)
    if series.has_publisher_code_number:
        code_number_formset = PublisherCodeNumberFormSet(request.POST or None)
    else:
        code_number_formset = None
    external_link_formset = ExternalLinkRevisionFormSet(request.POST or None)

    if request.method != 'POST':
        if variant_of:
            initial = dict(variant_of.__dict__)
            form = init_added_variant(form_class, initial, variant_of)
            credits = variant_of.active_credits.exclude(deleted=True)
            if credits:
                credits_formset = get_issue_revision_form_set_extra(
                  extra=credits.count()+1)(initial=credits.values(
                                           *credits[0].revisions.first()
                                           ._field_list()))
        else:
            initial = {}
            reversed_issues = series.active_issues().order_by('-sort_code')
            if reversed_issues.exists():
                initial['after'] = reversed_issues[0].id
            form = form_class(initial=initial)
        return _display_add_issue_form(request, series, form,
                                       credits_formset, code_number_formset,
                                       external_link_formset,
                                       variant_of, variant_cover)

    form = form_class(request.POST)
    if not form.is_valid() or not credits_formset.is_valid() \
       or not external_link_formset.is_valid():
        return _display_add_issue_form(request, series, form,
                                       credits_formset, code_number_formset,
                                       external_link_formset,
                                       variant_of, variant_cover)

    if variant_of and edit_with_base:
        kwargs = {'request': request,
                  'variant_of': variant_of,
                  'form': form}
        if variant_cover:
            return reserve(request, variant_cover.id, 'cover',
                           callback=add_variant_issuerevision,
                           callback_args=kwargs)
        return reserve(request, variant_of.id, 'issue',
                       callback=add_variant_issuerevision,
                       callback_args=kwargs)

    changeset = Changeset(indexer=request.user, state=states.OPEN,
                          change_type=CTYPES['issue_add'])
    changeset.save()
    revision = form.save(commit=False)
    revision.save_added_revision(changeset=changeset,
                                 series=series,
                                 variant_of=variant_of)
    form.save_m2m()
    extra_forms = {'credits_formset': credits_formset,
                   'code_number_formset': code_number_formset,
                   'external_link_formset': external_link_formset}
    revision.process_extra_forms(extra_forms)

    if variant_of:
        return edit(request, changeset.id)
    if 'copy_from_predecessor' in request.POST and revision.after:
        issue = revision.after
        if issue.variant_of:
            issue = issue.variant_of
        return HttpResponseRedirect(urlresolvers.reverse(
          'compare_issues_copy',
          kwargs={'issue_id': issue.id,
                  'issue_revision_id': revision.id}))

    return submit(request, changeset.id)


def add_variant_to_issue_revision(request, changeset_id, issue_revision_id):
    """
    Add a variant issue to an existing issue revision within a changeset.
    This view allows the changeset owner to add a variant of an issue to their
    existing issue revision. The variant inherits initial data from the base
    issue revision and can be customized with its own credits, publisher codes,
    and external links.

    Args:
        changeset_id: The ID of the changeset to add the variant to.
        issue_revision_id: The ID of the base issue revision that the variant
            will be associated with.

    Returns:
        HttpResponse: On GET, displays the add variant form with formsets for
            credits, publisher codes, and external links.
        HttpResponseRedirect: On successful POST, redirects to the changeset
            edit page. On cancel, redirects to the changeset edit page.
        HttpResponse: On validation error, redisplays the form with errors.

    Raises:
        Http404: If the changeset does not exist.

    Notes:
        - Variants cannot be added to changesets of type 'variant_add' or
          'two_issues'.
        - The changeset type is updated to 'variant_add' upon successful
          variant creation.
    """

    changeset = get_object_or_404(Changeset, id=changeset_id)
    if request.user != changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may add variants.')
    if changeset.change_type in [CTYPES['variant_add'], CTYPES['two_issues']]:
        return render_error(
          request, 'You cannot add a variant to this changeset.')
    issue_revision = changeset.issuerevisions.get(id=issue_revision_id)
    series = issue_revision.series

    form_class = get_revision_form(model_name='issue',
                                   series=series,
                                   publisher=issue_revision.series.publisher,
                                   variant_of=issue_revision.issue,
                                   user=request.user)
    credits_formset = IssueRevisionFormSet(request.POST or None)
    if series.has_publisher_code_number:
        code_number_formset = PublisherCodeNumberFormSet(request.POST or None)
    else:
        code_number_formset = None
    external_link_formset = ExternalLinkRevisionFormSet(request.POST or None)

    if request.method != 'POST':
        initial = dict(issue_revision.__dict__)
        form = init_added_variant(form_class, initial, issue_revision,
                                  revision=True)
        credits = issue_revision.issue_credit_revisions.exclude(deleted=True)
        if credits:
            credits_formset = get_issue_revision_form_set_extra(
              extra=credits.count() + 1)(initial=credits.values(
                                         *credits[0]._field_list()))
        return _display_add_issue_form(request, series, form, credits_formset,
                                       code_number_formset,
                                       external_link_formset, None, None,
                                       issue_revision=issue_revision)

    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit',
          kwargs={'id': changeset_id}))

    form = form_class(request.POST)
    if not form.is_valid():
        return _display_add_issue_form(request, series, form, credits_formset,
                                       code_number_formset,
                                       external_link_formset, None, None,
                                       issue_revision=issue_revision)

    variant_revision = form.save(commit=False)
    variant_revision.save_added_revision(changeset=changeset,
                                         series=issue_revision.series,
                                         variant_of=issue_revision.issue)
    form.save_m2m()
    extra_forms = {'credits_formset': credits_formset,
                   'code_number_formset': code_number_formset,
                   'external_link_formset': external_link_formset}
    variant_revision.process_extra_forms(extra_forms)
    changeset.change_type = CTYPES['variant_add']
    changeset.save()

    return HttpResponseRedirect(urlresolvers.reverse(
      'edit',
      kwargs={'id': changeset_id}))


def add_variant_issuerevision(changeset, revision, variant_of, form,
                              request):
    """
    Add a variant issue revision to a changeset.

    This function creates a new variant issue revision and associates it with
    the provided changeset. If the changeset is for a cover, it first reserves
    the original issue. The function then processes the form data, saves the
    issue revision, and handles related formsets for credits, publisher code
    numbers, and external links.

    Args:
        changeset: The changeset object to which the variant will be added.
        revision: The revision object (used when converting from cover).
        variant_of: The issue object that this variant is based on.
        form: The form containing the variant issue data.
        request: The HTTP request object containing POST data for formsets.
    Returns:
        bool: True if the variant was successfully added, False if the
                reservation failed (when processing a cover changeset).
    Side Effects:
        - Modifies the changeset's change_type to CTYPES['variant_add'].
        - Creates and saves an issue revision for the variant.
        - May create an issue reservation if the changeset is for a cover.
        - Processes and saves related formsets (credits, code numbers,
            external links).
    """

    issuerevision = form.save(commit=False)

    if changeset.change_type == CTYPES['cover']:
        # via create variant for cover
        issue = revision.issue

        # create issue revision for the issue of the cover
        if not _do_reserve(changeset.indexer, issue, 'issue',
                           changeset=changeset):
            return False

    changeset.change_type = CTYPES['variant_add']
    changeset.save()

    # save issue revision for the new variant record
    issuerevision.save_added_revision(changeset=changeset,
                                      series=variant_of.series,
                                      variant_of=variant_of)
    form.save_m2m()
    credits_formset = IssueRevisionFormSet(request.POST or None)
    if variant_of.series.has_publisher_code_number:
        code_number_formset = PublisherCodeNumberFormSet(request.POST or None)
    else:
        code_number_formset = None
    external_link_formset = ExternalLinkRevisionFormSet(request.POST or None)
    extra_forms = {'credits_formset': credits_formset,
                   'code_number_formset': code_number_formset,
                   'external_link_formset': external_link_formset}
    issuerevision.process_extra_forms(extra_forms)

    return True


@permission_required('indexer.can_reserve')
def add_variant_issue(request, issue_id, cover_id=None, edit_with_base=False):
    """
    Add a variant issue based on an existing issue.

    This view handles the creation of a variant issue by delegating to the
    add_issue function with variant-specific parameters. It validates that if
    a cover is provided, it corresponds to the selected issue.

    Args:
        issue_id: The ID of the base issue that this variant is based on.
        cover_id: Optional ID of a cover image to associate with the variant
                  issue. If provided, cover must be from the base issue.
        edit_with_base: Boolean flag indicating whether to edit the variant
                        in a changeset with the base issue. Defaults to False.

    Returns:
        HttpResponse: Either redirects to the add_issue view with appropriate
                      variant parameters, or returns an error response if the
                      cover doesn't correspond to the issue.

    Raises:
        Http404: If the issue or cover with the given ID does not exist.
    """
    if cover_id:
        cover = get_object_or_404(Cover, id=cover_id)
        if cover.issue.id != int(issue_id):
            return render_error(
              request, 'Selected cover does not correspond to selected issue.')
    else:
        cover = None
    issue = get_object_or_404(Issue, id=issue_id)

    if 'edit_with_base' in request.POST or edit_with_base:
        return add_issue(request, issue.series.id, variant_of=issue,
                         variant_cover=cover, edit_with_base=True)
    else:
        return add_issue(request, issue.series.id, variant_of=issue,
                         variant_cover=cover)


def _display_add_issue_form(request, series, form, credits_formset,
                            code_number_formset, external_link_formset,
                            variant_of, variant_cover, issue_revision=None):
    action_label = 'Submit New'
    alternative_action = None
    alternative_label = None

    if variant_of:
        kwargs = {
            'issue_id': variant_of.id,
        }
        if variant_cover:
            kwargs['cover_id'] = variant_cover.id
            action_label = 'Save New'
            object_name = 'Variant Issue'
            extra_adding_info = 'of %s and edit both' % variant_of
        else:
            alternative_action = 'edit_with_base'
            alternative_label = 'Save New Variant Issue For *%s* And Edit ' \
                                'Both' % variant_of
            object_name = 'Variant Issue'
            extra_adding_info = 'of %s' % variant_of

        url = urlresolvers.reverse('add_variant_issue', kwargs=kwargs)
    elif issue_revision:
        kwargs = {
            'issue_revision_id': issue_revision.id,
            'changeset_id': issue_revision.changeset.id,
        }
        action_label = 'Save New'
        url = urlresolvers.reverse('add_variant_to_issue_revision',
                                   kwargs=kwargs)
        object_name = 'Variant Issue'
        extra_adding_info = 'of %s' % issue_revision
    else:
        kwargs = {
            'series_id': series.id,
        }
        url = urlresolvers.reverse('add_issue', kwargs=kwargs)
        object_name = 'Issue'
        extra_adding_info = 'to %s' % series
        alternative_action = 'copy_from_predecessor'
        alternative_label = 'Submit New Issue And Copy From Predecessor'

    return oi_render(
      request, 'oi/edit/add_frame.html',
      {
        'object_name': object_name,
        'object_url': url,
        'extra_adding_info': extra_adding_info,
        'action_label': action_label,
        'form': form,
        'credits_formset': credits_formset,
        'code_number_formset': code_number_formset,
        'external_link_formset': external_link_formset,
        'alternative_action': alternative_action,
        'alternative_label': alternative_label,
      })


@permission_required('indexer.can_reserve')
def add_issues(request, series_id, method=None):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    issue_annotated = Changeset.objects.annotate(
      issue_revision_count=Count('issuerevisions'))
    issue_adds = issue_annotated.filter(issue_revision_count__gte=1) \
                                .filter(issuerevisions__issue=None) \
                                .filter(issuerevisions__series__id=series_id) \
                                .filter(state__in=states.ACTIVE)
    series = get_object_or_404(Series, id=series_id)
    if series.deleted or series.pending_deletion():
        return render_error(
          request, 'Cannot add issues '
          'since "%s" is deleted or pending deletion.' % series)

    if method is None:
        return oi_render(request, 'oi/edit/add_issues.html',
                         {'series': series,
                          'issue_adds': issue_adds})

    form_class = get_bulk_issue_revision_form(series=series, method=method,
                                              user=request.user)
    credits_formset = IssueRevisionFormSet(request.POST or None)

    if request.method != 'POST':
        reversed_issues = series.active_issues().order_by('-sort_code')
        initial = {}
        if reversed_issues.exists():
            initial['after'] = reversed_issues[0].id
        form = form_class(initial=initial)
        return _display_bulk_issue_form(request, series, form,
                                        credits_formset, method)

    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'show_series',
          kwargs={'series_id': series_id}))

    form = form_class(request.POST)
    if not form.is_valid() or not credits_formset.is_valid():
        return _display_bulk_issue_form(request, series, form,
                                        credits_formset, method)

    changeset = Changeset(indexer=request.user, state=states.OPEN,
                          change_type=CTYPES['issue_add'])
    changeset.save()
    if method == 'number':
        new_issues = _build_whole_numbered_issues(series, form, changeset)
    elif method == 'volume':
        new_issues = _build_per_volume_issues(series, form, changeset)
    elif method == 'year':
        new_issues = _build_per_year_issues(series, form, changeset)
    elif method == 'year_volume':
        new_issues = _build_per_year_volume_issues(series, form, changeset)
    else:
        return render_error(
          request, 'Unknown method for generating issues: %s' % method)

    # "after" for the rest of the issues gets set when they are all
    # committed to display.
    new_issues[0].after = form.cleaned_data['after']

    # Process editor credits from the formset - these will be cloned
    # to all issues
    credit_revisions_data = []
    for credit_form in credits_formset:
        if (credit_form.cleaned_data and
                not credit_form.cleaned_data.get('DELETE', False)):
            # Skip empty forms
            if ('creator' in credit_form.cleaned_data and
                    credit_form.cleaned_data['creator']):
                credit_revisions_data.append(credit_form.cleaned_data)

    for revision in new_issues:
        revision.save_added_revision(changeset=changeset, series=series)
        if form.cleaned_data['brand_emblem']:
            revision.brand_emblem.set(form.cleaned_data['brand_emblem'].all())
        if form.cleaned_data['indicia_printer']:
            revision.indicia_printer.set(form.cleaned_data['indicia_printer']
                                             .all())
        # Clone editor credits to each issue
        for credit_data in credit_revisions_data:
            credit = IssueCreditRevision(
                issue_revision=revision,
                creator=credit_data['creator'],
                credit_type=credit_data['credit_type'],
                is_credited=credit_data.get('is_credited', False),
                credited_as=credit_data.get('credited_as', ''),
                uncertain=credit_data.get('uncertain', False),
                credit_name=credit_data.get('credit_name', ''),
                is_sourced=credit_data.get('is_sourced', False),
                sourced_by=credit_data.get('sourced_by', ''),
                changeset=changeset
            )
            credit.save()
    return submit(request, changeset.id)


def _build_whole_numbered_issues(series, form, changeset):
    issue_revisions = []
    cd = form.cleaned_data
    first_number = cd['first_number']
    increment = 0
    for number in range(first_number, first_number + cd['number_of_issues']):
        issue_revisions.append(_build_issue(
          form,
          revision_sort_code=increment,
          number=number,
          volume=cd['volume'],
          no_volume=cd['no_volume'],
          display_volume_with_number=cd['display_volume_with_number']))
        increment += 1
    return issue_revisions


def _build_per_volume_issues(series, form, changeset):
    issue_revisions = []
    cd = form.cleaned_data
    first_number = cd['first_number']
    num_issues = cd['number_of_issues']
    per_volume = cd['issues_per_volume']
    current_volume = cd['first_volume']
    for increment in range(0, num_issues):
        current_number = (first_number + increment) % per_volume
        if current_number == 0:
            current_number = per_volume
        elif increment > 0 and current_number == 1:
            current_volume += 1
        issue_revisions.append(_build_issue(
          form,
          revision_sort_code=increment,
          number=current_number,
          volume=current_volume,
          no_volume=False,
          display_volume_with_number=True))
    return issue_revisions


def _build_per_year_issues(series, form, changeset):
    issue_revisions = []
    cd = form.cleaned_data
    first_number = cd['first_number']
    num_issues = cd['number_of_issues']
    per_year = cd['issues_per_year']
    current_year = cd['first_year']
    for increment in range(0, num_issues):
        current_number = (first_number + increment) % per_year
        if current_number == 0:
            current_number = per_year
        elif increment > 0 and current_number == 1:
            current_year += 1
        issue_revisions.append(_build_issue(
          form,
          revision_sort_code=increment,
          number='%d/%d' % (current_number, current_year),
          volume=cd['volume'],
          no_volume=cd['no_volume'],
          display_volume_with_number=cd['display_volume_with_number']))
    return issue_revisions


def _build_per_year_volume_issues(series, form, changeset):
    issue_revisions = []
    cd = form.cleaned_data
    first_number = cd['first_number']
    num_issues = cd['number_of_issues']
    per_cycle = cd['issues_per_cycle']
    current_year = cd['first_year']
    current_volume = cd['first_volume']
    for increment in range(0, num_issues):
        current_number = (first_number + increment) % per_cycle
        if current_number == 0:
            current_number = per_cycle
        elif increment > 0 and current_number == 1:
            current_year += 1
            current_volume += 1
        issue_revisions.append(_build_issue(
          form,
          revision_sort_code=increment,
          number='%d/%d' % (current_number, current_year),
          volume=current_volume,
          no_volume=False,
          display_volume_with_number=cd['display_volume_with_number']))
    return issue_revisions


def _build_issue(form, revision_sort_code, number,
                 volume, no_volume, display_volume_with_number):
    cd = form.cleaned_data
    # Don't specify series and changeset as save_added_revision handles that.
    return IssueRevision(
      number=number,
      volume=volume,
      no_volume=no_volume,
      display_volume_with_number=display_volume_with_number,
      indicia_publisher=cd['indicia_publisher'],
      indicia_pub_not_printed=cd['indicia_pub_not_printed'],
      no_brand=cd['no_brand'],
      indicia_frequency=cd['indicia_frequency'],
      no_indicia_frequency=cd['no_indicia_frequency'],
      price=cd['price'],
      page_count=cd['page_count'],
      page_count_uncertain=cd['page_count_uncertain'],
      editing=cd['editing'],
      no_editing=cd['no_editing'],
      no_isbn=cd['no_isbn'],
      no_barcode=cd['no_barcode'],
      rating=cd['rating'],
      no_rating=cd['no_rating'],
      revision_sort_code=revision_sort_code)


def _display_bulk_issue_form(request, series, form, credits_formset,
                             method=None):
    kwargs = {
        'series_id': series.id,
    }
    url_name = 'add_issues'
    if method is not None:
        kwargs['method'] = method
        url_name = 'add_multiple_issues'
    url = urlresolvers.reverse(url_name, kwargs=kwargs)
    extra_adding_info = 'to %s' % series
    return oi_render(
      request, 'oi/edit/add_frame.html',
      {
        'object_name': 'Issues',
        'object_url': url,
        'extra_adding_info': extra_adding_info,
        'action_label': 'Submit new',
        'form': form,
        'credits_formset': credits_formset,
      })


@permission_required('indexer.can_reserve')
def compare_issues_copy(request, issue_revision_id, issue_id):
    revision = get_object_or_404(IssueRevision, id=issue_revision_id)
    issue = get_object_or_404(Issue, id=issue_id)
    compare_revision = issue.revisions.filter(
      changeset__state=5,
      next_revision=None) | issue.revisions.filter(
      changeset__state=5,
      next_revision__changeset__state__lt=5)
    compare_revision = compare_revision.get()
    if request.method != 'POST':
        revision.compare_changes(compare_revision=compare_revision)
        field_list = revision.field_list()
        if 'after' in field_list:
            field_list.remove('after')
        field_list.remove('number')
        return oi_render(
          request, 'oi/edit/compare_and_copy.html',
          {
           'prev_rev': compare_revision,
           'revision': revision,
           'field_list': field_list
          }
        )
    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': revision.changeset_id}))

    selected_fields = request.POST.getlist('field_to_copy')
    fields_to_copy = revision._get_single_value_fields().copy()
    fields_to_copy.update(revision._get_meta_fields())
    fields_to_set = revision._get_multi_value_fields()
    for field in selected_fields:
        # single value fields
        if field in fields_to_copy:
            setattr(revision, field, getattr(compare_revision, field))
        # m2m fields
        if field in fields_to_set:
            getattr(revision, field).clear()
            getattr(revision, field).add(*list(getattr(compare_revision,
                                                       field).all()))
    if 'year_on_sale' in selected_fields:
        revision.year_on_sale = compare_revision.year_on_sale
    if 'month_on_sale' in selected_fields:
        revision.month_on_sale = compare_revision.month_on_sale
    if 'day_on_sale' in selected_fields:
        revision.day_on_sale = compare_revision.day_on_sale
    revision.save()

    if 'editing' in selected_fields:
        credits = compare_revision.issue_credit_revisions.exclude(deleted=True)
        existing_credits = revision.issue_credit_revisions\
                                   .exclude(deleted=True)
        for credit in credits:
            q_vals = {}
            for field in credit._get_single_value_fields():
                q_vals[field] = getattr(credit, field)
            credit_revision = revision.issue_credit_revisions.filter(
                                       Q(**q_vals), deleted=False)
            if credit_revision:
                existing_credits = existing_credits.exclude(
                  id=credit_revision[0].id)
            else:
                new_credit = IssueCreditRevision.clone(
                  credit, revision.changeset,
                  fork=True, issue_revision=revision)
                existing_credits = existing_credits.exclude(
                  id=new_credit.id)

        for existing_credit in existing_credits:
            if existing_credit.issue_credit:
                existing_credit.deleted = True
                existing_credit.save()
            else:
                existing_credit.delete()

    return HttpResponseRedirect(
        urlresolvers.reverse('edit_revision',
                             kwargs={'model_name': 'issue',
                                     'id': revision.id}))




def add_feature(request):
    return add_generic(request, 'feature')


@permission_required('indexer.can_reserve')
def add_feature_logo(request, feature_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    feature = get_object_or_404(Feature, id=feature_id, deleted=False)

    if feature.pending_deletion():
        return render_error(
          request,
          'Cannot add a feature logo since "%s" is pending deletion.'
          % feature)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'show_feature', kwargs={'feature_id': feature_id}))

    initial = {'feature': feature}
    form = get_feature_logo_revision_form(
      user=request.user)(request.POST or None,
                         request.FILES or None,
                         initial=initial)

    if form.is_valid():
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['feature_logo'])
        changeset.save()
        revision = form.save(commit=False)
        revision.save_added_revision(changeset=changeset)
        form.save_m2m()
        # TODO make generic
        if revision.image_revision:
            revision.image_revision.changeset = changeset
            revision.image_revision.object_id = revision.id
            revision.image_revision.content_type = ContentType\
                                   .objects.get_for_model(revision)
            revision.image_revision.save()

        return submit(request, changeset.id)

    object_name = 'Feature Logo'
    object_url = urlresolvers.reverse('add_feature_logo',
                                      kwargs={'feature_id': feature.id})

    return oi_render(
      request, 'oi/edit/add_frame.html',
      {
        'object_name': object_name,
        'object_url': object_url,
        'action_label': 'Submit new',
        'form': form,
      })


@permission_required('indexer.can_reserve')
def add_feature_relation(request, feature_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    feature = get_object_or_404(Feature, id=feature_id, deleted=False)

    if feature.pending_deletion():
        return render_error(request, 'Cannot add Relation for '
                                     'feature "%s" since the record is '
                                     'pending deletion.' % feature)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
                'show_feature', kwargs={'feature_id': feature_id}))

    initial = {}
    initial['from_feature'] = feature
    relation_form = get_feature_relation_revision_form(
      user=request.user)(request.POST or None, initial=initial)

    if relation_form.is_valid():
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['feature_relation'])
        changeset.save()

        revision = relation_form.save(commit=False)
        revision.save_added_revision(changeset=changeset, feature=feature)
        revision.save()

        return submit(request, changeset.id)

    context = {'form': relation_form,
               'object_name': 'Relation with Feature',
               'object_url': urlresolvers.reverse('add_feature_relation',
                                                  kwargs={'feature_id':
                                                          feature_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


def add_story_arc(request):
    return add_generic(request, 'story_arc')


@permission_required('indexer.can_reserve')
def add_story_arc_relation(request, story_arc_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    story_arc = get_object_or_404(StoryArc, id=story_arc_id, deleted=False)

    if story_arc.pending_deletion():
        return render_error(request, 'Cannot add Relation for '
                                     'story arc "%s" since the record is '
                                     'pending deletion.' % story_arc)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
                'show_story_arc', kwargs={'story_arc_id': story_arc_id}))

    initial = {}
    initial['from_story_arc'] = story_arc
    relation_form = get_story_arc_relation_revision_form(
      user=request.user)(request.POST or None, initial=initial)

    if relation_form.is_valid():
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['story_arc_relation'])
        changeset.save()

        revision = relation_form.save(commit=False)
        revision.save_added_revision(changeset=changeset, story_arc=story_arc)
        revision.save()

        return submit(request, changeset.id)

    context = {'form': relation_form,
               'object_name': 'Relation with Story Arc',
               'object_url': urlresolvers.reverse('add_story_arc_relation',
                                                  kwargs={'story_arc_id':
                                                          story_arc_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


def add_universe(request):
    return add_generic(request, 'universe')


# TODO: add extra_forms to add_generic
# could work with extra_forms_name and extra_form in call to it
# needs also changes in add_frame-template
# compare the following with add_generic


@permission_required('indexer.can_reserve')
def add_character(request):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse('add'))

    form = get_revision_form(model_name='character',
                             user=request.user)(request.POST or None)
    character_names_formset = CharacterRevisionFormSet(request.POST or None)
    external_link_formset = ExternalLinkRevisionFormSet(request.POST or None)

    if not form.is_valid() or not character_names_formset.is_valid()\
       or not external_link_formset.is_valid():
        return oi_render(
          request, 'oi/edit/add_frame.html',
          {
            'object_name': 'Character',
            'object_url': urlresolvers.reverse('add_character'),
            'action_label': 'Submit new',
            'form': form,
            'character_names_formset': character_names_formset,
            'external_link_formset': external_link_formset,
          })
    else:
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['character'])
        changeset.save()
        revision = form.save(commit=False)
        revision.save_added_revision(changeset=changeset)
        extra_forms = {'character_names_formset': character_names_formset,
                       'external_link_formset': external_link_formset}
        revision.process_extra_forms(extra_forms)
        return submit(request, changeset.id)


@permission_required('indexer.can_reserve')
def add_character_relation(request, character_id):
    character = get_object_or_404(Character, id=character_id, deleted=False)

    if character.pending_deletion():
        return render_error(request, 'Cannot add Relation for '
                                     'character "%s" since the record is '
                                     'pending deletion.' % character)

    initial = {}
    initial['from_character'] = character_id
    initial['language_code'] = character.language.code

    cancel = urlresolvers.reverse('show_character',
                                  kwargs={'character_id': character_id})
    object_url = urlresolvers.reverse('add_character_relation',
                                      kwargs={'character_id': character_id})
    return add_generic(request,
                       'character_relation',
                       initial=initial,
                       object_url=object_url,
                       object_name='Relation with Character',
                       cancel=cancel)


def add_group(request):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse('add'))

    form = get_revision_form(model_name='group',
                             user=request.user)(request.POST or None)
    group_names_formset = GroupRevisionFormSet(request.POST or None)

    if not form.is_valid() or not group_names_formset.is_valid():
        return oi_render(
          request, 'oi/edit/add_frame.html',
          {
            'object_name': 'Group',
            'object_url': urlresolvers.reverse('add_group'),
            'action_label': 'Submit new',
            'form': form,
            'group_names_formset': group_names_formset,
          })
    else:
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['group'])
        changeset.save()
        revision = form.save(commit=False)
        revision.save_added_revision(changeset=changeset)
        extra_forms = {'group_names_formset': group_names_formset}
        revision.process_extra_forms(extra_forms)
        return submit(request, changeset.id)


@permission_required('indexer.can_reserve')
def add_group_relation(request, group_id):
    group = get_object_or_404(Group, id=group_id, deleted=False)

    if group.pending_deletion():
        return render_error(request, 'Cannot add Relation for '
                                     'group "%s" since the record is '
                                     'pending deletion.' % group)

    initial = {}
    initial['from_group'] = group_id
    initial['language_code'] = group.language.code

    cancel = urlresolvers.reverse('show_group',
                                  kwargs={'group_id': group_id})
    object_url = urlresolvers.reverse('add_group_relation',
                                      kwargs={'group_id': group_id})
    return add_generic(request,
                       'group_relation',
                       initial=initial,
                       object_url=object_url,
                       object_name='Relation with Character',
                       cancel=cancel)


@permission_required('indexer.can_reserve')
def add_group_membership(request, character_id):
    character = get_object_or_404(Character, id=character_id, deleted=False)

    if character.pending_deletion():
        return render_error(request, 'Cannot add Group Membership '
                                     'since character"%s" is deleted or '
                                     'pending deletion.' % character)

    initial = {}
    initial['character'] = character.id
    initial['language_code'] = character.language.code

    cancel = urlresolvers.reverse('show_character',
                                  kwargs={'character_id': character_id})
    object_url = urlresolvers.reverse('add_group_membership',
                                      kwargs={'character_id': character_id})
    return add_generic(request,
                       'group_membership',
                       initial=initial,
                       object_url=object_url,
                       object_name='Group Membership for a Character',
                       cancel=cancel)


@permission_required('indexer.can_reserve')
def add_group_member(request, group_id):
    group = get_object_or_404(Group, id=group_id, deleted=False)

    if group.pending_deletion():
        return render_error(request, 'Cannot add Members '
                                     'since group "%s" is deleted or '
                                     'pending deletion.' % group)

    initial = {}
    initial['group'] = group_id
    initial['language_code'] = group.language.code
    cancel = urlresolvers.reverse('show_group',
                                  kwargs={'group_id': group_id})
    object_url = urlresolvers.reverse('add_group_member',
                                      kwargs={'group_id': group_id})
    return add_generic(request,
                       'group_membership',
                       initial=initial,
                       object_url=object_url,
                       object_name='a Member to a Group',
                       cancel=cancel)


@permission_required('indexer.can_reserve')
def add_story(request, issue_revision_id, changeset_id):
    changeset = get_object_or_404(Changeset, id=changeset_id)
    if request.user != changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may add stories.')
    # check if this is a request to add a copy of a sequence
    if 'copy' in request.GET or 'copy_cover' in request.GET:
        issue_revision = changeset.issuerevisions.get(id=issue_revision_id)
        seq = request.GET.get('added_sequence_number')
        initial = _get_initial_add_story_data(request, issue_revision, seq)
        if 'copy_cover' in request.GET:
            cover = True
        else:
            cover = False
        return copy_sequence(request, issue_revision_id,
                             sequence_number=initial['sequence_number'],
                             cover=cover)

    if request.method == 'POST' and 'cancel_return' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': changeset_id}))

    # Process add form if this is a POST.
    try:
        issue_revision = changeset.issuerevisions.get(id=issue_revision_id)
        issue = issue_revision.issue
        if issue_revision.variant_of and \
           issue_revision.active_stories().count():
            return render_error(
              request,
              'You cannot add more than one story to a variant issue.',
              redirect=False)

        initial = {}
        if request.method != 'POST':
            seq = ''
            if 'added_sequence_number' in request.GET:
                seq = request.GET['added_sequence_number']
            if seq == '':
                return render_error(
                  request,
                  'You must supply a sequence number for the new story.',
                  redirect=False)
            else:
                initial = _get_initial_add_story_data(request, issue_revision,
                                                      seq)
        form = get_story_revision_form(
          user=request.user,
          issue_revision=issue_revision)(request.POST or None,
                                         initial=initial)
        credits_formset = StoryRevisionFormSet(request.POST or None)
        characters_formset = StoryCharacterRevisionFormSet(
          request.POST or None)
        groups_formset = StoryGroupRevisionFormSet(
          request.POST or None)

        if not form.is_valid() or not credits_formset.is_valid() or \
           not characters_formset.is_valid():
            kwargs = {
                'issue_revision_id': issue_revision_id,
                'changeset_id': changeset_id,
            }
            url = urlresolvers.reverse('add_story', kwargs=kwargs)

            if hasattr(form, 'cleaned_data'):
                StoryRevision.extra_forms_errors(
                  request, form, {'credits_formset': credits_formset,
                                  'characters_formset': characters_formset,
                                  'groups_formset': groups_formset
                                  })

            return oi_render(
                request, 'oi/edit/add_frame.html',
                {
                    'object_name': 'Story',
                    'object_url': url,
                    'action_label': 'Save',
                    'form': form,
                    'settings': settings,
                    'credits_formset': credits_formset,
                    'characters_formset': characters_formset,
                    'groups_formset': groups_formset
                })

        revision = form.save(commit=False)
        stories = issue_revision.active_stories()
        _reorder_children(request, issue_revision, stories, 'sequence_number',
                          stories, commit=True, unique=False, skip=revision)

        revision.save_added_revision(changeset=changeset,
                                     issue=issue)
        revision.save()
        form.save_characters(revision)

        if form.cleaned_data['comments']:
            revision.comments.create(commenter=request.user,
                                     changeset=changeset,
                                     text=form.cleaned_data['comments'],
                                     old_state=changeset.state,
                                     new_state=changeset.state)

        extra_forms = {'credits_formset': credits_formset,
                       'characters_formset': characters_formset,
                       'groups_formset': groups_formset}
        revision.process_extra_forms(extra_forms)
        form.save_m2m()
        revision.post_form_save()

        if revision.feature_logo.exists():
            # stories for variants in variant-add next to issue have issue
            if revision.issue:
                language = revision.issue.series.language
            else:
                language = revision.my_issue_revision. \
                    other_issue_revision.series.language
            for feature_logo in revision.feature_logo.all():
                if feature_logo.feature.get(language=language) not in \
                  revision.feature_object.all():
                    revision.feature_object.add(feature_logo.feature.
                                                get(language=language))

        if revision.source_class == Story \
           and revision.type.id == STORY_TYPES['about comics']:
            biblio_revision = BiblioEntryRevision(
              storyrevision_ptr=revision)
            biblio_revision.__dict__.update(revision.__dict__)
            biblio_revision.save()
            return HttpResponseRedirect(
              urlresolvers.reverse('edit_revision',
                                   kwargs={'model_name': 'biblio_entry',
                                           'id': biblio_revision.id}))
        if 'create_appearance_order' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
              'create_character_order_revision',
              kwargs={'story_revision_id': revision.id, 'type_id': 1}))
        if 'create_importance_order' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
              'create_character_order_revision',
              kwargs={'story_revision_id': revision.id, 'type_id': 2}))

        return HttpResponseRedirect(urlresolvers.reverse('edit',
                                    kwargs={'id': changeset.id}))

    except ViewTerminationError as vte:
        return vte.response

    except (IssueRevision.DoesNotExist, IssueRevision.MultipleObjectsReturned):
        return render_error(
          request,
          'Could not find issue revision for id ' + issue_revision_id)


def _get_initial_add_story_data(request, issue_revision, seq):
    # First, if we have an integer sequence number, make certain it's
    # not a duplicate as we can't tell if they meant above or below.
    # Since all sequence numbers in the database are integers,
    # if we have a non-int then we know it's not a dupe.
    try:
        seq_num = int(seq)
        if issue_revision.story_set.filter(sequence_number=seq_num)\
                                   .count():
            raise ViewTerminationError(render_error(
              request,
              "New stories must be added with a sequence number that "
              "is not already in use.  You may use a decimal number "
              "to insert a sequence between two existing sequences, "
              "or a negative number to insert before sequence zero.",
              redirect=False))

    except ValueError:
        try:
            float_num = float(seq)
        except ValueError:
            raise ViewTerminationError(render_error(
              request,
              "Sequence number must be a number.", redirect=False))

        # Now convert to the next int above the float.  If this
        # is a duplicate that's OK because we know that the user
        # intended the new sequence to go *before* the existing one.
        # int(float) truncates towards zero, hence adding 1 to positive
        # float values.
        if float_num > 0:
            float_num += 1
        seq_num = int(float_num)

    initial = {'no_editing': True}
    if seq_num == 0 and issue_revision.series.is_comics_publication:
        # Do not default other sequences, because if we do we
        # will get a lot of people leaving the default values
        # by accident.  Only sequence zero is predictable.
        initial['type'] = StoryType.objects.get(name='cover').id
        initial['no_script'] = True

    initial['sequence_number'] = seq_num
    return initial


@permission_required('indexer.can_reserve')
def copy_story_revision(request, issue_revision_id, changeset_id=None,
                        story_revision_id=None):
    if request.method != 'POST':
        changeset = get_object_or_404(Changeset, id=changeset_id)
        issue_revision = changeset.issuerevisions.get()
        if issue_revision.id != int(issue_revision_id):
            raise ViewTerminationError(render_error(
                                       request,
                                       'Error in accessing this routine.',
                                       redirect=False))
    else:
        issue_revision = IssueRevision.objects.get(id=issue_revision_id)
        changeset = issue_revision.changeset
    if request.user != changeset.indexer:
        raise ViewTerminationError(
          render_error(request,
                       'Only the reservation holder may add stories.',
                       redirect=False))
    if request.method != 'POST':
        # pick sequence to copy
        try:
            sequence_number = int(request.GET['copied_sequence_number'])
        except ValueError:
            raise ViewTerminationError(render_error(
                                    request,
                                    "Sequence number must be a number.",
                                    redirect=False))
        try:
            story_revision = changeset.storyrevisions.get(
              sequence_number=sequence_number)
        except StoryRevision.DoesNotExist:
            raise ViewTerminationError(render_error(
              request,
              "Sequence with this number does not exist.",
              redirect=False))
        story = PreviewStory.init(story_revision)
        return oi_render(request, 'oi/edit/confirm_copy_sequence.html',
                         {'issue_revision': issue_revision,
                          'story': story,
                          'story_revision': story_revision
                          })
    else:
        if 'cancel' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit', kwargs={'id': changeset.id}))
        story_revision = changeset.storyrevisions.get(id=story_revision_id)
        copy_credit_info = request.POST.get('copy_credit_info', False)
        copy_characters = request.POST.get('copy_characters', False)
        rev = StoryRevision.clone_revision(story_revision, changeset,
                                           issue_revision=issue_revision,
                                           copy_credit_info=copy_credit_info,
                                           copy_characters=copy_characters)

        return HttpResponseRedirect(urlresolvers.reverse(
          'edit_revision', kwargs={'id': rev.id, 'model_name': 'story'}))


@permission_required('indexer.can_reserve')
def story_select_compare(request, story_revision_id):
    revision = get_object_or_404(StoryRevision, id=story_revision_id)
    if request.user != revision.changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may access this page.')
    cached_stories = get_cached_stories(request)
    cached_covers = get_cached_covers(request)
    other_revisions = revision.changeset.storyrevisions.exclude(id=revision.id)
    return oi_render(
        request, 'oi/edit/select_story_for_copy.html',
        {'revision': revision, 'cached_stories': cached_stories,
         'cached_covers': cached_covers, 'other_revisions': other_revisions})


@permission_required('indexer.can_reserve')
def compare_stories_copy(request, story_revision_id, story_id=None,
                         other_revision_id=None):
    """
    Compare and copy story revision fields from another story or story
    revision.

    This view allows an indexer to compare their current story revision with
    either:
    - An approved story (via story_id)
    - Another story revision (via other_revision_id)

    The indexer can then selectively copy fields from the comparison source
    to their revision.

    Args:
        request: The HTTP request object
        story_revision_id: ID of the current story revision being edited
        story_id: Optional ID of an approved story to compare against
        other_revision_id: Optional ID of another story revision to compare
                           against

    Returns:
        - GET: Renders comparison page with fields that can be copied
        - POST with 'cancel': Redirects to changeset edit page
        - POST with field selections: Copies selected fields and redirects to
          revision edit page

    Raises:
        Http404: If the story revision, story, or other revision is not found

    Permission Required:
        indexer.can_reserve

    Notes:
        - Only the changeset indexer can access this page
        - Handles copying of:
            - Single-value fields
            - Multi-value (m2m) fields
            - Keywords (with special handling)
            - Story credits (with optional qualifier copying)
            - Characters and groups (with language-aware handling)
        - When copying characters/groups between different languages, attempts
          to find appropriate translations
        - Removes existing credits/characters/groups that weren't in the
          source when copying
    """
    revision = get_object_or_404(StoryRevision, id=story_revision_id)
    if request.user != revision.changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may access this page.')
    if story_id:
        story = get_object_or_404(Story, id=story_id)
        compare_revision = story.revisions.filter(
          changeset__state=5,
          next_revision=None) | story.revisions.filter(
          changeset__state=5,
          next_revision__changeset__state__lt=5)
        compare_revision = compare_revision.get()
    if other_revision_id:
        compare_revision = get_object_or_404(StoryRevision,
                                             id=other_revision_id)
    if request.method != 'POST':
        revision.compare_changes(compare_revision=compare_revision)
        field_list = revision.field_list()
        field_list.remove('sequence_number')
        return oi_render(
          request, 'oi/edit/compare_and_copy.html',
          {
           'prev_rev': compare_revision,
           'revision': revision,
           'field_list': field_list,
           'is_story': True
          }
        )
    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': revision.changeset_id}))

    selected_fields = request.POST.getlist('field_to_copy')
    fields_to_copy = revision._get_single_value_fields().copy()
    fields_to_copy.update(revision._get_meta_fields())
    fields_to_set = revision._get_multi_value_fields()
    for field in selected_fields:
        # single value fields
        if field in fields_to_copy:
            setattr(revision, field, getattr(compare_revision, field))
        # m2m fields
        if field in fields_to_set:
            getattr(revision, field).clear()
            getattr(revision, field).add(*list(getattr(compare_revision,
                                                       field).all()))
        # special handling for keywords due to their different storage
        # in data_objects vs. revision
        if field == 'keywords':
            setattr(revision, field, getattr(compare_revision, field))
    revision.save()

    if 'copy_select_with_qualifiers' in request.POST:
        exclude = {'is_sourced', 'sourced_by'}
    else:
        exclude = {'is_credited', 'credited_as', 'is_signed', 'signed_as',
                   'signature', 'is_sourced', 'sourced_by', 'credit_name'}

    for credit_type in CREDIT_TYPES:
        if credit_type in selected_fields:
            credit_type_id = CREDIT_TYPES[credit_type]
            credits = compare_revision.story_credit_revisions\
                                      .filter(credit_type_id=credit_type_id)\
                                      .exclude(deleted=True)
            existing_credits = revision.story_credit_revisions\
                                       .filter(credit_type_id=credit_type_id)\
                                       .exclude(deleted=True)
            # following is similar to process_extra_forms
            for credit in credits:
                blank_values = credit._get_blank_values()
                q_vals = {}
                # match depends on copy_select_with_qualifiers
                for field in credit._get_single_value_fields():
                    if field in exclude:
                        q_vals[field] = blank_values[field]
                    else:
                        q_vals[field] = getattr(credit, field)
                credit_revision = revision.story_credit_revisions.filter(
                                        Q(**q_vals), deleted=False)
                if credit_revision:
                    existing_credits = existing_credits.exclude(
                      id=credit_revision[0].id)
                else:
                    new_credit = StoryCreditRevision.clone(
                      credit,
                      revision.changeset,
                      fork=True,
                      story_revision=revision,
                      exclude=exclude)
                    existing_credits = existing_credits.exclude(
                      id=new_credit.id)
            for existing_credit in existing_credits:
                if existing_credit.story_credit:
                    existing_credit.deleted = True
                    existing_credit.save()
                else:
                    existing_credit.delete()
    if revision.issue and (compare_revision.issue.series.language ==
                           revision.issue.series.language):
        same_language = True
    else:
        same_language = False

    if 'characters' in selected_fields:
        characters = compare_revision.story_character_revisions\
                                     .exclude(deleted=True)
        existing_characters = revision.story_character_revisions\
                                      .exclude(deleted=True)

        for character in characters:
            if same_language:
                q_vals = {}
                for field in character._get_single_value_fields():
                    q_vals[field] = getattr(character, field)
                character_revision = revision.story_character_revisions.filter(
                                        Q(**q_vals), deleted=False)
                if character_revision:
                    existing_characters = existing_characters.exclude(
                      id=character_revision[0].id)
                    character_revision[0].group_name.set(character.group_name
                                                                  .all())
                else:
                    new_character = StoryCharacterRevision.clone(
                      character,
                      revision.changeset,
                      fork=True,
                      story_revision=revision)
                    existing_characters = existing_characters.exclude(
                      id=new_character.id)
            else:
                new_character_revision = \
                  StoryCharacterRevision.copied_translation(character,
                                                            revision)
                if new_character_revision:
                    existing_characters = existing_characters.exclude(
                      id=new_character_revision.id)

        for existing_character in existing_characters:
            if existing_character.story_character:
                existing_character.deleted = True
                existing_character.save()
            else:
                existing_character.delete()

        groups = compare_revision.story_group_revisions\
                                 .exclude(deleted=True)
        existing_groups = revision.story_group_revisions\
                                  .exclude(deleted=True)
        for group in groups:
            if same_language:
                q_vals = {}
                for field in group._get_single_value_fields():
                    q_vals[field] = getattr(group, field)
                group_revision = revision.story_group_revisions.filter(
                                          Q(**q_vals), deleted=False)
                if group_revision:
                    existing_groups = existing_groups.exclude(
                      id=group_revision[0].id)
                else:
                    new_group = StoryGroupRevision.clone(
                      group, revision.changeset, fork=True,
                      story_revision=revision)
                    existing_groups = existing_groups.exclude(
                      id=new_group.id)
            else:
                language = revision.issue.series.language

                translations = group.group_name.group.translations(language)
                if translations.count() == 0 and \
                   group.group_name.group.translated_from():
                    translations = group.group_name.group.translated_from()\
                                                   .translations(language)
                if translations.count() == 1:
                    group.group_name = translations.get().official_name()
                    new_group = StoryGroupRevision.clone(
                      group, revision.changeset, fork=True,
                      story_revision=revision)
                    existing_groups = existing_groups.exclude(
                      id=new_group.id)

        for existing_group in existing_groups:
            if existing_group.story_group:
                existing_group.deleted = True
                existing_group.save()
            else:
                existing_group.delete()

    return HttpResponseRedirect(
        urlresolvers.reverse('edit_revision',
                             kwargs={'model_name': 'story',
                                     'id': revision.id}))


@permission_required('indexer.can_reserve')
def edit_character_order_revision(request, story_revision_id, type_id):
    story_revision = get_object_or_404(StoryRevision, id=story_revision_id)
    changeset = get_object_or_404(Changeset, id=story_revision.changeset_id)
    if request.user != changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may edit character orders.')
    type = get_object_or_404(CharacterOrderType, id=type_id)
    if not story_revision.character_order_revisions.filter(type=type).exists():
        return render_error(
          request,
          'A character order of type "%s" does not exist for story "%s".'
          % (type.name, story_revision))
    return HttpResponseRedirect(urlresolvers.reverse(
      'reorder_characters',
      kwargs={'character_order_id':
              story_revision.character_order_revisions.get(type=type).id}))


@permission_required('indexer.can_reserve')
def create_character_order_revision(request, story_revision_id, type_id):
    story_revision = get_object_or_404(StoryRevision, id=story_revision_id)
    changeset = get_object_or_404(Changeset, id=story_revision.changeset_id)
    if request.user != changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may create character orders.')
    type = get_object_or_404(CharacterOrderType, id=type_id)
    if story_revision.character_order_revisions.filter(type=type).exists():
        return render_error(
          request,
          'A character order of type "%s" already exists for story "%s".'
          % (type.name, story_revision))
    order_revision = CharacterOrderRevision(
      story_revision=story_revision,
      type=type,
      changeset=changeset)
    order_revision.save()
    return HttpResponseRedirect(urlresolvers.reverse(
      'reorder_characters',
      kwargs={'character_order_id': order_revision.id}))

##############################################################################
# Series Bond Editing
##############################################################################


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


##############################################################################
# Reprint Link Editing
##############################################################################


def parse_reprint(reprints):
    """ parse a reprint entry for exactly our standard """
    reprint_direction_from = ["from", "da", "di", "de", "uit", "från", "aus"]
    reprint_direction_to = ["in", "i"]
    from_to = reprints.split(' ')[0].lower()
    if from_to in reprint_direction_from + reprint_direction_to:
        try:  # our format: seriesname (publisher, year <series>) #nr
            position = reprints.find(' (')
            series = reprints[len(from_to) + 1:position]
            string = reprints[position + 2:]
            end_bracket = string.find(')')
            position = string[:end_bracket].rfind(', ')
            if position < 0:
                series_pos = string.lower().find('series)')
                if series_pos > 0:
                    position = string[:series_pos].rfind(', ')
            publisher = string[:position].strip()
            position += 2
            string = string[position:]
            year = string[:4]

            # italian and spanish from/in
            if from_to in ['da ', 'in ', 'de ', 'en ']:
                if year.isdecimal() is not True:
                    position = string.find(')')
                    year = string[position-4:position]
            string = string[4:]
            position = string.find(' #')
            if position > 0 and len(string[position+2:]):

                string = string[position + 2:]
                position = string.find(' [')  # check for notes
                if position > 0:
                    date_pos = string.find(' (')  # check for (date)
                    if date_pos > 0 and date_pos < position:
                        position = date_pos
                else:
                    position = string.find(' (')  # check for (date)
                    if position > 0:  # if found ignore later
                        pass
                volume = None
                if string.isdecimal():  # in this case we are fine
                    number = string
                elif string[0].lower() == 'v' and string.find('#') > 0:
                    n_pos = string.find('#')
                    volume = string[1:n_pos]
                    if position > 0:
                        number = string[n_pos+1:position]
                    else:
                        number = string[n_pos+1:]
                else:
                    hyphen = string.find(' -')
                    # following issue title after number
                    if hyphen > 0 and string[:hyphen].isdecimal() and \
                       not string[hyphen+2:].strip()[0].isdecimal():
                        number = string[:hyphen]
                    else:
                        if position > 0:
                            number = string[:position].strip('., ')
                        else:
                            number = string.strip('., ')
                if number == 'nn':
                    number = '[nn]'
                if number == '?':
                    number = None
            else:
                number = None
                volume = None
            return publisher, series, year, number, volume
        except ValueError:
            pass
    return None, None, None, None, None


@permission_required('indexer.can_reserve')
def list_issue_reprints(request, id):
    issue_revision = get_object_or_404(IssueRevision, id=id)
    changeset = issue_revision.changeset
    if request.user != changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may access this page.')
    try:
        response = oi_render(
          request, 'oi/edit/list_issue_reprints.html',
          {'issue_revision': issue_revision, 'changeset': changeset})
    except NoReverseMatch:
        return render_error(
          request,
          'A reprint notes entry is malformed, most likely for one sequence '
          'it contains linebreaks, which are not supported for this field.')
    response['Cache-Control'] = "no-cache, no-store, "\
                                "max-age=0, must-revalidate"
    return response


@permission_required('indexer.can_reserve')
def reserve_reprint(request, changeset_id, reprint_id):
    changeset = get_object_or_404(Changeset, id=changeset_id)
    if request.user != changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may access this page.')
    if 'edit_origin' in request.POST:
        which_side = 'origin'
    elif 'edit_origin_internal' in request.POST:
        which_side = 'origin_internal'
    elif 'edit_target' in request.POST:
        which_side = 'target'
    elif 'edit_target_internal' in request.POST:
        which_side = 'target_internal'
    elif 'flip_direction' in request.POST:
        which_side = 'flip_direction'
    elif 'delete' in request.POST:
        which_side = 'delete'
    elif 'matching_sequence' in request.POST:
        which_side = 'matching_sequence'
    elif 'edit_note_origin' in request.POST:
        which_side = 'edit_note_origin'
    elif 'edit_note_target' in request.POST:
        which_side = 'edit_note_target'
    else:
        return _cant_get(request)
    display_obj = get_object_or_404(DISPLAY_CLASSES['reprint'],
                                    id=reprint_id)
    revision_lock = _get_revision_lock(display_obj, changeset)
    if not revision_lock:
        return render_error(
          request,
          'Cannot edit "%s" as it is already reserved.' % display_obj)

    revision = ReprintRevision.clone(display_obj, changeset=changeset)

    return HttpResponseRedirect(urlresolvers.reverse(
      'edit_reprint', kwargs={'id': revision.id, 'which_side': which_side}))


@permission_required('indexer.can_reserve')
def edit_reprint(request, id, which_side=None):
    reprint_revision = get_object_or_404(ReprintRevision, id=id)
    changeset = reprint_revision.changeset
    if request.user != changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may access this page.')

    if not which_side:
        if 'edit_origin' in request.POST:
            which_side = 'origin'
        elif 'edit_origin_internal' in request.POST:
            which_side = 'origin_internal'
        elif 'edit_target' in request.POST:
            which_side = 'target'
        elif 'edit_target_internal' in request.POST:
            which_side = 'target_internal'
        elif 'flip_direction' in request.POST:
            which_side = 'flip_direction'
        elif 'delete' in request.POST:
            which_side = 'delete'
        elif 'restore' in request.POST:
            which_side = 'restore'
        elif 'remove' in request.POST:
            which_side = 'remove'
        elif 'matching_sequence' in request.POST:
            which_side = 'matching_sequence'
        elif 'edit_note_origin' in request.POST:
            which_side = 'edit_note_origin'
        elif 'edit_note_target' in request.POST:
            which_side = 'edit_note_target'
        else:
            return _cant_get(request)

    changeset_issue = changeset.issuerevisions.get()

    issue = None
    story = None
    story_revision = None
    if which_side.startswith('origin'):
        if reprint_revision.origin:
            select_issue = reprint_revision.origin_issue
            sequence_number = reprint_revision.origin.sequence_number
        elif reprint_revision.origin_issue:
            select_issue = reprint_revision.origin_issue
            sequence_number = None
        elif which_side == 'origin_internal':
            select_issue = reprint_revision.origin_revision.issue
        else:  # for newly added stories problematic otherwise
            raise NotImplementedError
        issue = reprint_revision.target_issue
        if reprint_revision.target:
            story = reprint_revision.target
        else:
            story_revision = reprint_revision.target_revision
    elif which_side.startswith('target'):
        if reprint_revision.target:
            select_issue = reprint_revision.target.issue
            sequence_number = reprint_revision.target.sequence_number
        elif reprint_revision.target_issue:
            select_issue = reprint_revision.target_issue
            sequence_number = None
        elif which_side == 'target_internal':
            select_issue = reprint_revision.target_revision.issue
        else:  # for newly added stories problematic otherwise
            raise NotImplementedError
        issue = reprint_revision.origin_issue
        if reprint_revision.origin:
            story = reprint_revision.origin
        else:
            story_revision = reprint_revision.origin_revision
    elif which_side == 'flip_direction':
        origin = reprint_revision.target
        origin_revision = reprint_revision.target_revision
        origin_issue = reprint_revision.target_issue
        reprint_revision.target = reprint_revision.origin
        reprint_revision.target_revision = reprint_revision.origin_revision
        reprint_revision.target_issue = reprint_revision.origin_issue
        reprint_revision.origin = origin
        reprint_revision.origin_revision = origin_revision
        reprint_revision.origin_issue = origin_issue
        reprint_revision.save()
        return HttpResponseRedirect(urlresolvers.reverse(
          'list_issue_reprints', kwargs={'id': changeset_issue.id}))
    elif which_side == 'delete':
        reprint_revision.deleted = True
        reprint_revision.save()
        return HttpResponseRedirect(urlresolvers.reverse(
          'list_issue_reprints', kwargs={'id': changeset_issue.id}))
    elif which_side == 'restore':
        if reprint_revision.deleted:
            reprint_revision.deleted = False
            reprint_revision.save()
            return HttpResponseRedirect(
                urlresolvers.reverse('list_issue_reprints',
                                     kwargs={'id': changeset_issue.id}))
        else:
            return _cant_get(request)
    elif which_side == 'remove':
        return HttpResponseRedirect(
          urlresolvers.reverse('remove_reprint_revision', kwargs={'id': id}))
    elif which_side == 'matching_sequence':
        if reprint_revision.origin:
            story = reprint_revision.origin
            issue = reprint_revision.target_issue
        else:
            story = reprint_revision.target
            issue = reprint_revision.origin_issue
        if issue != changeset_issue.issue:
            return _cant_get(request)
        return HttpResponseRedirect(
          urlresolvers.reverse('create_matching_sequence',
                               kwargs={'reprint_revision_id': id,
                                       'story_id': story.id,
                                       'issue_id': issue.id}))
        raise ValueError
    elif which_side.startswith('edit_note'):
        if which_side == 'edit_note_origin':
            which_side = 'target'
            if reprint_revision.origin:
                story = reprint_revision.origin
                story_story = True
                story_revision = False
                issue = None
            elif reprint_revision.origin_revision:
                story = PreviewStory.init(reprint_revision.origin_revision)
                story_story = False
                story_revision = True
                issue = None
            else:
                story = None
                story_story = False
                story_revision = False
                issue = reprint_revision.origin_issue
            if reprint_revision.target:
                selected_story = reprint_revision.target
                selected_issue = None
            else:
                selected_story = None
                selected_issue = reprint_revision.target_issue
        else:
            which_side = 'origin'
            if reprint_revision.target:
                story = reprint_revision.target
                story_story = True
                story_revision = False
                issue = None
            elif reprint_revision.target_revision:
                story = PreviewStory.init(reprint_revision.target_revision)
                story_story = False
                story_revision = True
                issue = None
            else:
                story = None
                story_story = False
                story_revision = False
                issue = reprint_revision.target_issue
            if reprint_revision.origin:
                selected_story = reprint_revision.origin
                selected_issue = None
            else:
                selected_story = None
                selected_issue = reprint_revision.origin_issue

        return oi_render(request, 'oi/edit/confirm_reprint.html',
                         {
                          'story': story,
                          'issue': issue,
                          'story_story': story_story,
                          'story_revision': story_revision,
                          'selected_story': selected_story,
                          'selected_issue': selected_issue,
                          'reprint_revision': reprint_revision,
                          'reprint_revision_id': reprint_revision.id,
                          'changeset': changeset,
                          'which_side': which_side
                         })
    else:
        raise NotImplementedError

    if which_side.endswith('internal'):
        issue_revision = select_issue.revisions.get(changeset=changeset)
        return oi_render(
          request, 'oi/edit/select_internal_object.html',
          {'issue_revision': issue_revision, 'changeset': changeset,
           'reprint_revision': reprint_revision,
           'which_side': which_side[:6]})

    initial = {'series': select_issue.series.name,
               'publisher': select_issue.series.publisher.name,
               'year': select_issue.series.year_began,
               'number': select_issue.number,
               'sequence_number': sequence_number}
    if story or story_revision:
        if story:
            story_id = story.id
            story_revision_id = None
        else:
            story_id = None
            story_revision_id = story_revision.id
            story = story_revision
        issue_id = None
        heading = 'Select story/issue for the reprint link with %s of %s' \
                  % (esc(story), esc(story.issue))
    else:
        story_id = None
        issue_id = issue.id
        story_revision_id = None
        heading = 'Select story/issue for the reprint link with %s' \
                  % (esc(issue))
    data = {'story_id': story_id,
            'story_revision_id': story_revision_id,
            'issue_id': issue_id,
            'reprint_revision_id': reprint_revision.id,
            'changeset_id': changeset.id,
            'story': True,
            'issue': True,
            'initial': initial,
            'heading': mark_safe('<h2>%s</h2>' % heading),
            'target': 'a story or issue',
            'return': 'confirm_reprint',
            'which_side': which_side,
            'cancel': urlresolvers.reverse('edit',
                                           kwargs={'id': changeset.id})}
    select_key = store_select_data(request, None, data)
    return HttpResponseRedirect(urlresolvers.reverse(
      'select_object', kwargs={'select_key': select_key}))


@permission_required('indexer.can_reserve')
def add_reprint(request, changeset_id,
                story_id=None, issue_id=None, reprint_note=''):
    if story_id:
        story = get_object_or_404(StoryRevision, id=story_id,
                                  changeset__id=changeset_id)
    else:
        issue = get_object_or_404(IssueRevision, id=issue_id,
                                  changeset__id=changeset_id)
    if reprint_note:
        publisher, series, year, number, volume = \
            parse_reprint(unquote(reprint_note).split(';')[0])
        initial = {'series': series, 'publisher': publisher,
                   'year': year, 'number': number}
    else:
        initial = {}
    if story_id:
        heading = 'Select story/issue for the reprint link with %s of %s' \
                                    % (esc(story), esc(story.issue))
    else:
        heading = 'Select story/issue for the reprint link with %s' \
                                    % (esc(issue))
    data = {'story_revision_id': story_id,
            'issue_revision_id': issue_id,
            'changeset_id': changeset_id,
            'story': True,
            'issue': True,
            'initial': initial,
            'heading': mark_safe('<h2>%s</h2>' % heading),
            'target': 'a story or issue',
            'return': 'confirm_reprint',
            'cancel': urlresolvers.reverse('edit',
                                           kwargs={'id': changeset_id})}
    select_key = store_select_data(request, None, data)
    return HttpResponseRedirect(urlresolvers.reverse(
      'select_object', kwargs={'select_key': select_key}))


@permission_required('indexer.can_reserve')
def select_internal_object(request, id, changeset_id, which_side,
                           issue_id=None, story_id=None):
    reprint_revision = get_object_or_404(ReprintRevision, id=id)
    if reprint_revision.changeset.id != int(changeset_id):
        return _cant_get(request)
    changeset = reprint_revision.changeset
    if request.user != changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may access this page.')
    if which_side == 'origin':
        if reprint_revision.target:
            other_story = reprint_revision.target
            other_issue = None
        elif reprint_revision.target_issue:
            other_issue = reprint_revision.target_issue
            other_story = None
        else:
            raise NotImplementedError
    elif which_side == 'target':
        if reprint_revision.origin:
            other_story = reprint_revision.origin
            other_issue = None
        elif reprint_revision.origin_issue:
            other_issue = reprint_revision.origin_issue
            other_story = None
        else:
            raise NotImplementedError
    else:
        return _cant_get(request)

    if issue_id:
        this_issue = get_object_or_404(IssueRevision, id=issue_id)
        this_story = None
    else:
        this_story = get_object_or_404(StoryRevision, id=story_id)
        this_story = PreviewStory.init(this_story)
        this_issue = None

    return oi_render(request, 'oi/edit/confirm_internal.html',
                     {
                      'this_issue': this_issue, 'this_story': this_story,
                      'other_issue': other_issue, 'other_story': other_story,
                      'changeset': changeset,
                      'reprint_revision_id': reprint_revision.id,
                      'reprint_revision': reprint_revision,
                      'which_side': which_side})


def _selected_copy_sequence(request, data, object_type, selected_id):
    if request.method != 'POST':
        return _cant_get(request)
    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': data['changeset_id']}))
    issue_revision = get_object_or_404(IssueRevision,
                                       id=data['issue_revision_id'])
    story = get_object_or_404(Story, id=selected_id)
    return oi_render(request, 'oi/edit/confirm_copy_sequence.html',
                     {
                      'issue_revision': issue_revision,
                      'story': story,
                      'sequence_number': data['sequence_number'],
                     })


@permission_required('indexer.can_reserve')
def copy_sequence(request, issue_revision_id, story_id=None,
                  sequence_number=None, cover=False):
    issue_revision = get_object_or_404(IssueRevision, id=issue_revision_id)
    if request.user != issue_revision.changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may access this page.')

    if cover:
        story = False
    else:
        story = True

    if request.method != 'POST':
        heading = 'Select story to copy into %s' % (esc(issue_revision))
        data = {'issue_revision_id': issue_revision_id,
                'changeset_id': issue_revision.changeset_id,
                'story': story,
                'cover': cover,
                'initial': {},
                'heading': mark_safe('<h2>%s</h2>' % heading),
                'target': 'a story',
                'return': '_selected_copy_sequence',
                'sequence_number': sequence_number,
                'cancel': urlresolvers.reverse('edit', kwargs={
                            'id': issue_revision.changeset_id})}
        select_key = store_select_data(request, None, data)
        return HttpResponseRedirect(urlresolvers.reverse('select_object',
                                    kwargs={'select_key': select_key}))
    else:
        issue_revision = get_object_or_404(IssueRevision, id=issue_revision_id)
        if 'cancel' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit', kwargs={'id': issue_revision.changeset_id}))
        story = get_object_or_404(Story, id=story_id)
        copy_credit_info = request.POST.get('copy_credit_info', False)
        copy_characters = request.POST.get('copy_characters', False)
        story_revision = StoryRevision.copied_revision(
          story, issue_revision.changeset, issue_revision=issue_revision,
          copy_credit_info=copy_credit_info, copy_characters=copy_characters)
        # sequence number should be determined in add_story
        # but this routine could be called differently as well
        if sequence_number is not None:
            story_revision.sequence_number = sequence_number
            story_revision.save()
            stories = issue_revision.active_stories()\
                                    .exclude(id=story_revision.id)
            if sequence_number < 0:
                story_revision.sequence_number = 0
                story_revision.save()
            _reorder_children(request, issue_revision, stories,
                              'sequence_number',
                              stories, commit=True, unique=False,
                              skip=story_revision)
        return HttpResponseRedirect(urlresolvers.reverse('edit_revision',
                                    kwargs={'model_name': 'story',
                                            'id': story_revision.id}))


@permission_required('indexer.can_reserve')
def create_matching_sequence(request, reprint_revision_id, story_id, issue_id,
                             edit=False, qualifier=False):  # noqa: F811
    story = get_object_or_404(Story, id=story_id)
    issue = get_object_or_404(Issue, id=issue_id)
    reprint_revision = get_object_or_404(ReprintRevision,
                                         id=reprint_revision_id)
    changeset = reprint_revision.changeset
    changeset_issue = changeset.issuerevisions.get()
    if request.user != changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may access this page.')
    if issue != changeset_issue.issue:
        return _cant_get(request)
    if request.method != 'POST' and not edit:
        if story == reprint_revision.origin:
            direction = 'from'
        else:
            direction = 'in'
        return oi_render(
          request, 'oi/edit/create_matching_sequence.html',
          {'issue': issue, 'story': story,
           'reprint_revision': reprint_revision, 'direction': direction})
    else:
        # we have two ways to get here, without edit it comes from the
        # reprint overview page, which has a confirm page and the
        # selection of what to copy in the POST
        if qualifier:
            copy_credit_info = True
        elif edit:
            copy_credit_info = False
        else:
            copy_credit_info = request.POST.get('copy_credit_info', False)
        if edit:
            copy_characters = True
        else:
            copy_characters = request.POST.get('copy_characters', False)
        story_revision = StoryRevision.copied_revision(
          story, changeset, issue_revision=changeset_issue,
          copy_credit_info=copy_credit_info, copy_characters=copy_characters)
        if reprint_revision.origin:
            reprint_revision.target_revision = story_revision
            reprint_revision.target_issue = None
        else:
            reprint_revision.origin_revision = story_revision
            reprint_revision.origin_issue = None
        reprint_revision.save()
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit_revision',
          kwargs={'model_name': 'story',
                  'id': story_revision.id}))


@permission_required('indexer.can_reserve')
def confirm_reprint(request, data, object_type, selected_id):
    if request.method != 'POST':
        return _cant_get(request)
    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': data['changeset_id']}))

    if 'story_id' in data and data['story_id']:
        story = get_object_or_404(Story, id=data['story_id'])
        story_revision = False
        story_story = True
        current_issue = None
    elif 'story_revision_id' in data and data['story_revision_id']:
        story_story = False
        story_revision = True
        story_revision = get_object_or_404(StoryRevision,
                                           id=data['story_revision_id'],
                                           changeset__id=data['changeset_id'])
        story = PreviewStory.init(story_revision)
        current_issue = None
    elif 'issue_id' in data and data['issue_id']:
        story_story = False
        story_revision = False
        story = None
        current_issue = get_object_or_404(Issue, id=data['issue_id'])
    elif 'issue_revision_id' in data and data['issue_revision_id']:
        story_story = False
        story_revision = False
        story = None
        current_issue = get_object_or_404(IssueRevision,
                                          id=data['issue_revision_id'])
        current_issue = current_issue.issue
    else:
        raise NotImplementedError

    changeset = get_object_or_404(Changeset, id=data['changeset_id'])

    if object_type == 'story':
        selected_story = get_object_or_404(Story, id=selected_id)
        selected_issue = None
    else:
        selected_story = None
        selected_issue = get_object_or_404(Issue, id=selected_id)

    if 'reprint_revision_id' in data:
        reprint_revision = get_object_or_404(ReprintRevision,
                                             id=data['reprint_revision_id'])
        reprint_revision_id = data['reprint_revision_id']
    else:
        reprint_revision_id = None
        reprint_revision = None

    if 'which_side' in data:
        which_side = data['which_side']
    elif 'which_side' in request.session:
        which_side = request.session['which_side']
    else:
        which_side = None

    return oi_render(request, 'oi/edit/confirm_reprint.html',
                     {
                      'story': story,
                      'issue': current_issue,
                      'story_story': story_story,
                      'story_revision': story_revision,
                      'selected_story': selected_story,
                      'selected_issue': selected_issue,
                      'reprint_revision': reprint_revision,
                      'reprint_revision_id': reprint_revision_id,
                      'changeset': changeset,
                      'which_side': which_side
                     })


@permission_required('indexer.can_reserve')
def save_reprint(request, reprint_revision_id, changeset_id,
                 story_one_id=None, story_revision_id=None, issue_one_id=None,
                 story_two_id=None, issue_two_id=None):
    if request.method != 'POST':
        return _cant_get(request)
    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': changeset_id}))
    if story_one_id and (story_revision_id or issue_one_id):
        return _cant_get(request)
    if story_two_id and issue_two_id:
        return _cant_get(request)
    if reprint_revision_id.isdecimal():
        revision = get_object_or_404(ReprintRevision, id=reprint_revision_id)
        if revision.changeset.id != int(changeset_id):
            return _cant_get(request)
    else:
        revision = None

    changeset = get_object_or_404(Changeset, id=changeset_id)

    origin = None
    origin_revision = None
    origin_issue = None
    target = None
    target_revision = None
    target_issue = None

    if story_revision_id:
        story_revision = StoryRevision.objects.get(id=story_revision_id)
        if 'reprint_notes' in request.POST:
            story_revision.reprint_notes = request.POST['reprint_notes']
        story_revision.save()
        if story_revision.story:
            story_one_id = story_revision.story.id
            story_revision_id = None

    if request.POST['direction'] == 'from':
        if story_one_id:
            target = Story.objects.get(id=story_one_id)
            target_issue = target.issue
        elif story_revision_id:
            target_revision = story_revision
            target_issue = target_revision.issue
        else:
            target_issue = Issue.objects.get(id=issue_one_id)
        if story_two_id:
            origin = Story.objects.get(id=story_two_id)
        else:
            origin_issue = Issue.objects.get(id=issue_two_id)
    else:
        if story_one_id:
            origin = Story.objects.get(id=story_one_id)
            origin_issue = origin.issue
        elif story_revision_id:
            origin_revision = story_revision
            origin_issue = origin_revision.issue
        else:
            origin_issue = Issue.objects.get(id=issue_one_id)
        if story_two_id:
            target = Story.objects.get(id=story_two_id)
        else:
            target_issue = Issue.objects.get(id=issue_two_id)

    notes = request.POST['reprint_link_notes']
    if revision:
        revision.origin = origin
        revision.origin_revision = origin_revision
        revision.origin_issue = origin_issue
        revision.target = target
        revision.target_revision = target_revision
        revision.target_issue = target_issue
        revision.notes = notes
        revision.save()
    else:
        revision = ReprintRevision(origin=origin,
                                   origin_revision=origin_revision,
                                   origin_issue=origin_issue,
                                   target=target,
                                   target_revision=target_revision,
                                   target_issue=target_issue,
                                   notes=notes)
        revision.save_added_revision(changeset=changeset)
        if request.POST['direction'] == 'from':
            request.session['which_side'] = 'origin'
        else:
            request.session['which_side'] = 'target'

    if request.POST['comments'].strip():
        revision.comments.create(commenter=request.user,
                                 changeset=changeset,
                                 text=request.POST['comments'],
                                 old_state=changeset.state,
                                 new_state=changeset.state)
    if 'add_reprint_view' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'list_issue_reprints',
          kwargs={'id': changeset.issuerevisions.get().id}))
    if 'matching_sequence' in request.POST or \
       'matching_sequence_with_qualifiers' in request.POST:
        if revision.origin:
            story = revision.origin
            issue = revision.target_issue
        else:
            story = revision.target
            issue = revision.origin_issue
        if issue != changeset.issuerevisions.get().issue:
            return _cant_get(request)
        if 'matching_sequence_with_qualifiers' in request.POST:
            return HttpResponseRedirect(
              urlresolvers.reverse('create_edit_matching_sequence_qualifier',
                                   kwargs={'reprint_revision_id': revision.id,
                                           'story_id': story.id,
                                           'issue_id': issue.id}))
        else:
            return HttpResponseRedirect(
              urlresolvers.reverse('create_edit_matching_sequence',
                                   kwargs={'reprint_revision_id': revision.id,
                                           'story_id': story.id,
                                           'issue_id': issue.id}))
    else:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': changeset_id}))


@permission_required('indexer.can_reserve')
def remove_reprint_revision(request, id):
    reprint = get_object_or_404(ReprintRevision, id=id)
    if request.user != reprint.changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may remove stories.')

    if reprint.source:
        return _cant_get(request)

    if reprint.origin:
        origin = reprint.origin
        origin_issue = None
    elif reprint.origin_revision:
        origin = PreviewStory.init(reprint.origin_revision)
        origin_issue = None
    else:
        origin = None
        origin_issue = reprint.origin_issue
    if reprint.target:
        target = reprint.target
        target_issue = None
    elif reprint.target_revision:
        target = PreviewStory.init(reprint.target_revision)
        target_issue = None
    else:
        target = None
        target_issue = reprint.target_issue

    if request.method != 'POST':
        return oi_render(request, 'oi/edit/confirm_remove_reprint.html',
                         {
                          'origin': origin,
                          'origin_issue': origin_issue,
                          'target': target,
                          'target_issue': target_issue,
                          'reprint': reprint
                         })

    # we fully delete the freshly added link, but first check if a
    # comment is attached.
    if reprint.comments.exists():
        comment = reprint.comments.latest('created')
        comment.text += '\nThe ReprintRevision "%s" for which this comment '\
                        'was entered was removed.' % reprint
        comment.revision_id = None
        comment.save()
    elif reprint.changeset.approver:
        # changeset already was submitted once since it has an approver
        # TODO not quite sure if we actually should add this comment
        reprint.changeset.comments.create(
          commenter=reprint.changeset.indexer,
          text='The ReprintRevision "%s" was removed.'
               % reprint,
          old_state=reprint.changeset.state,
          new_state=reprint.changeset.state)
    reprint.delete()
    return HttpResponseRedirect(urlresolvers.reverse(
      'list_issue_reprints',
      kwargs={'id': reprint.changeset.issuerevisions.get().id}))

##############################################################################
# Moving Items
##############################################################################


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


@permission_required('indexer.can_reserve')
def move_issue(request, issue_revision_id, series_id):
    """ move issue to series """
    issue_revision = get_object_or_404(IssueRevision, id=issue_revision_id,
                                       deleted=False)
    if request.user != issue_revision.changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may move issues.')

    if series_id == 0:
        if 'series_id' in request.GET:
            try:
                series_id = int(request.GET['series_id'])
            except ValueError:
                return render_error(request,
                                    'Series id must be an integer number.',
                                    redirect=False)
        else:
            return render_error(request,
                                'No series id given.',
                                redirect=False)
    series = Series.objects.filter(id=series_id, deleted=False)
    if not series:
        return render_error(request, 'No series with id %s.'
                            % series_id, redirect=False)
    series = series[0]

    if request.method != 'POST':
        header_text = "Do you want to move %s to %s ?" % \
          (issue_revision.issue.full_name(), series.full_name())
        url = urlresolvers.reverse(
          'move_issue',
          kwargs={'issue_revision_id': issue_revision_id,
                  'series_id': series_id})
        cancel_button = "Cancel"
        confirm_button = "move of issue %s to series %s" % (
          issue_revision.issue, series)
        return oi_render(request, 'oi/edit/confirm.html',
                                  {
                                    'type': 'Issue Move',
                                    'header_text': header_text,
                                    'url': url,
                                    'cancel_button': cancel_button,
                                    'confirm_button': confirm_button,
                                  })
    else:
        if 'cancel' not in request.POST:
            if issue_revision.series.publisher != series.publisher:
                for brand in issue_revision.brand_emblem.all():
                    new_brand = series.publisher.active_brand_emblems()\
                                                .filter(name=brand.name)
                    if new_brand.count() == 1:
                        issue_revision.brand_emblem.add(new_brand[0])
                    issue_revision.brand_emblem.remove(brand)
                if issue_revision.indicia_publisher:
                    new_indicia_publisher = series.publisher\
                                                  .active_indicia_publishers()\
                        .filter(name=issue_revision.indicia_publisher.name)
                    if new_indicia_publisher.count() == 1:
                        issue_revision.indicia_publisher = \
                            new_indicia_publisher[0]
                    else:
                        issue_revision.indicia_publisher = None
                        issue_revision.no_indicia_publisher = False
            issue_revision.series = series
            issue_revision.save()
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': issue_revision.changeset.id}))


@permission_required('indexer.can_reserve')
def move_story_revision(request, id):
    """ move story revision between two issue revisions """
    story = get_object_or_404(StoryRevision, id=id)
    if request.user != story.changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may move stories.')

    if story.changeset.issuerevisions.count() != 2:
        return render_error(
          request, 'Stories can only be moved between two issues.')

    if request.method != 'POST':
        return _cant_get(request)

    new_issue = story.changeset.issuerevisions.exclude(issue=story.issue).get()
    story.issue = new_issue.issue

    # In a two issue changeset (so far) one cannot add/edit reprints, but
    # reprint_revisions might exist from a move of the story before, free them.
    for reprint_revision in story.changeset.reprintrevisions.filter(
      target=story.story):
        _free_revision_lock(reprint_revision.reprint)
        reprint_revision.delete()
    for reprint_revision in story.changeset.reprintrevisions.filter(
      target_revision=story):
        _free_revision_lock(reprint_revision.reprint)
        reprint_revision.delete()
    for reprint_revision in story.changeset.reprintrevisions.filter(
      origin=story.story):
        _free_revision_lock(reprint_revision.reprint)
        reprint_revision.delete()
    for reprint_revision in story.changeset.reprintrevisions.filter(
      origin_revision=story):
        _free_revision_lock(reprint_revision.reprint)
        reprint_revision.delete()

    # Only when moving to a new variant or new issue do we need to handle
    # reprints. No reprint handling when in a change we move a sequence back,
    # which was moved in the change to the other side.
    if story.story and (not new_issue.issue
                        or new_issue.issue != story.story.issue):
        reprints = []
        for reprint in story.story.from_all_reprints.all():
            if _do_reserve(story.changeset.indexer,
                           reprint, 'reprint',
                           changeset=story.changeset):
                reprint_revision = reprint.revisions.get(
                  changeset__id=story.changeset.id)
                if new_issue.issue:
                    reprint_revision.target_issue = new_issue.issue
                    reprint_revision.target_revision = story
                    reprint_revision.target = None
                else:
                    # Keep reprint_revision.target so that the reprints
                    # show in the compare. Needs care in checks in save.
                    reprint_revision.target_issue = None
                    reprint_revision.target_revision = story
                reprint_revision.save()
                reprints.append(reprint_revision)
            else:
                for reprint_revision in reprints:
                    _free_revision_lock(reprint_revision.reprint)
                    reprint_revision.delete()
                return show_error_with_return(
                    request, 'Error while reserving reprints.',
                    story.changeset)
        for reprint in story.story.to_all_reprints.all():
            if _do_reserve(story.changeset.indexer,
                           reprint, 'reprint',
                           changeset=story.changeset):
                reprint_revision = reprint.revisions.get(
                  changeset__id=story.changeset.id)
                if new_issue.issue:
                    reprint_revision.origin_issue = new_issue.issue
                    reprint_revision.origin_revision = story
                    reprint_revision.origin = None
                else:
                    # Keep reprint_revision.origin so that the reprints
                    # show in the compare. Needs care in checks in save.
                    reprint_revision.origin_issue = None
                    reprint_revision.origin_revision = story
                reprint_revision.save()
                reprints.append(reprint_revision)
            else:
                for reprint_revision in reprints:
                    _free_revision_lock(reprint_revision.reprint)
                    reprint_revision.delete()
                return show_error_with_return(
                    request, 'Error while reserving reprints.',
                    story.changeset)

    story.sequence_number = new_issue.next_sequence_number()
    story.save()
    old_issue = story.changeset.issuerevisions.exclude(id=new_issue.id).get()

    _reorder_children(request, old_issue, old_issue.active_stories(),
                      'sequence_number', old_issue.active_stories(),
                      commit=True, unique=False)

    return HttpResponseRedirect(urlresolvers.reverse(
      'edit', kwargs={'id': story.changeset.id}))


@permission_required('indexer.can_reserve')
def move_cover(request, id, cover_id=None):
    """ move cover between two issue revisions """
    changeset = get_object_or_404(Changeset, id=id)
    if request.user != changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may move covers in a changeset.')

    if changeset.issuerevisions.count() != 2:
        return render_error(
          request, 'Covers can only be moved between two issues.')

    if request.method != 'POST':
        covers = []
        for revision in changeset.issuerevisions.all():
            if revision.issue and revision.issue.has_covers():
                for image in get_image_tags_per_issue(
                  revision.issue,
                  "current covers", ZOOM_MEDIUM, as_list=True):
                    image.append(revision)
                    covers.append(image)
        return oi_render(
          request,
          'oi/edit/move_covers.html',
          {
              'changeset': changeset,
              'covers': covers,
              'table_width': UPLOAD_WIDTH
          })

    cover = get_object_or_404(Cover, id=cover_id)
    issue = changeset.issuerevisions.filter(issue=cover.issue)
    if not issue:
        return render_error(
          request, 'Cover does not belong to an issue of this changeset.')

    revision_lock = _get_revision_lock(cover, changeset)
    if not revision_lock:
        return render_error(
          request, 'Cannot move the cover as it is already reserved.')

    # create cover revision
    revision = CoverRevision.objects.clone_revision(cover, changeset=changeset)

    return HttpResponseRedirect(urlresolvers.reverse(
      'edit', kwargs={'id': changeset.id}))


@permission_required('indexer.can_reserve')
def undo_move_cover(request, id, cover_id):
    changeset = get_object_or_404(Changeset, id=id)
    if request.user != changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may undo cover moves in a changeset.')

    if request.method != 'POST':
        return _cant_get(request)
    # TODO FIXME
    cover_revision = get_object_or_404(CoverRevision, id=cover_id,
                                       changeset=changeset)
    _free_revision_lock(cover_revision.cover)
    cover_revision.delete()

    return HttpResponseRedirect(urlresolvers.reverse(
      'edit', kwargs={'id': changeset.id}))

##############################################################################
# Removing Items from a Changeset
##############################################################################


@permission_required('indexer.can_reserve')
def remove_story_revision(request, id):
    story = get_object_or_404(StoryRevision, id=id)
    if request.user != story.changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may remove stories.')

    # if user manually tries to permanently remove a sequence revision
    # that came from a pre-existing sequence, toggle the deleted flag
    # instead
    if story.source:
        return toggle_delete_story_revision(request, id)

    if request.method != 'POST':
        preview_story = PreviewStory.init(story)
        return oi_render(
          request, 'oi/edit/remove_story_revision.html',
          {
            'story': preview_story,
            'issue': story.issue
          })

    # we fully delete the freshly added sequence, but first check if a
    # comment is attached.
    if story.comments.exists():
        comment = story.comments.latest('created')
        # might be set anyway. But if we don't set it we would get <span ...
        # in the response and we cannot mark a comment as safe.
        if not story.page_count:
            story.page_count_uncertain = True
        comment.text += '\nThe StoryRevision "%s" for which this comment was'\
                        ' entered was removed.' % show_revision_short(
                          story, markup=False)
        comment.revision_id = None
        comment.save()
    elif story.changeset.approver:
        # changeset already was submitted once since it has an approver
        # TODO not quite sure if we actually should add this comment
        story.changeset.comments.create(
          commenter=story.changeset.indexer,
          text='The StoryRevision "%s" was removed.'
               % show_revision_short(story, markup=False),
          old_state=story.changeset.state,
          new_state=story.changeset.state)
    story.delete()
    return HttpResponseRedirect(urlresolvers.reverse('edit',
                                kwargs={'id': story.changeset.id}))


@permission_required('indexer.can_reserve')
def toggle_delete_story_revision(request, id):
    story = get_object_or_404(StoryRevision, id=id)
    if request.user != story.changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may delete or restore stories.')

    story.toggle_deleted()
    return HttpResponseRedirect(urlresolvers.reverse('edit',
                                kwargs={'id': story.changeset.id}))

##############################################################################
# Ongoing Reservations
##############################################################################


@permission_required('indexer.can_reserve')
def ongoing(request, user_id=None):
    """
    Handle the ongoing reservation, process the request and form and
    return with error or success message as appropriate.
    """
    if request.method != 'POST':
        return _cant_get(request)

    if request.user.ongoing_reservations.count() >= \
       request.user.indexer.max_ongoing:
        return render_error(
          request, 'You have reached the maximum number of '
          'ongoing reservations you can hold at this time.  If you are a new '
          'user this number is very low or even zero, but will increase as '
          'your first few changes are approved.',
          redirect=False)

    series = get_object_or_404(Series, id=request.POST['series'])
    if series.deleted or series.pending_deletion():
        return render_error(
          request, 'Cannot reserve issues '
          'since "%s" is deleted or pending deletion.' % series)

    if request.method == 'POST':
        form = OngoingReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.indexer = request.user
            reservation.save()
            return HttpResponseRedirect(urlresolvers.reverse(
              'show_series', kwargs={'series_id': reservation.series.id}))
        else:
            return render_error(
              request, 'Something went wrong while reserving'
              ' the series. Please contact us if this error persists.')


def delete_ongoing(request, series_id):
    if request.method != 'POST':
        return render_error(
          request,
          'You must access this page through the proper form.')
    reservation = get_object_or_404(OngoingReservation, series=series_id)
    if request.user != reservation.indexer:
        return render_error(
          request,
          'Only the reservation holder may delete the reservation.')
    series = reservation.series
    reservation.delete()
    return HttpResponseRedirect(urlresolvers.reverse(
      'show_series', kwargs={'series_id': series.id}))

##############################################################################
# Reordering
##############################################################################




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


@permission_required('indexer.can_reserve')
def reorder_stories(request, issue_id, changeset_id):
    changeset = get_object_or_404(Changeset, id=changeset_id)
    if request.user != changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may reorder stories.')

    # At this time, only existing issues can have their stories reordered.
    # This is analogous to issues needing to exist before stories can be added.
    issue_revision = changeset.issuerevisions.get(issue=issue_id)
    if request.method != 'POST':
        return oi_render(request, 'oi/edit/reorder_stories.html',
                         {'issue': issue_revision, 'changeset': changeset})

    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': changeset_id}))

    try:
        stories = _process_reorder_form(request, issue_revision,
                                        'sequence_number',
                                        'story', StoryRevision)
        _reorder_children(request, issue_revision, stories,
                          'sequence_number', issue_revision.active_stories(),
                          commit=True, unique=False)

        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': changeset_id}))

    except ViewTerminationError as vte:
        return vte.response


@permission_required('indexer.can_reserve')
def reorder_characters(request, character_order_id):
    character_order_revision = get_object_or_404(CharacterOrderRevision,
                                                 id=character_order_id)
    changeset = character_order_revision.changeset
    if request.user != changeset.indexer:
        return render_error(
          request,
          'Only the reservation holder may reorder characters.')

    if request.method != 'POST':
        return oi_render(request, 'oi/edit/reorder_characters.html',
                         {'character_order': character_order_revision})

    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit_revision',
          kwargs={'id': character_order_revision.story_revision.id,
                  'model_name': 'story'}))

    try:
        order_code_boundary = request.POST['order_code_boundary']
        request_post = request.POST.copy()
        for key in request.POST:
            if key.startswith('order_code_') and key != 'order_code_boundary':
                value = request.POST[key]
                if value and float(value) >= float(order_code_boundary):
                    request_post.pop(key)
                    character_id = int(key.split('_')[-1])
                    revision_characters = character_order_revision\
                        .character_revisions
                    if revision_characters.filter(id=character_id).exists():
                        revision_characters.remove(character_id)
        request.POST = request_post
        characters = _process_reorder_form(request, character_order_revision,
                                           'order_code',
                                           'character', StoryCharacterRevision)
        order = 0
        for character in characters:
            revision_characters = character_order_revision.character_revisions
            if not revision_characters.filter(id=character.id).exists():
                revision_characters.add(character,
                                        through_defaults={'order_code': order})
            else:
                through_instance = revision_characters.through.objects.get(
                    order=character_order_revision,
                    story_character=character
                )
                through_instance.order_code = order
                through_instance.save()
            order += 1
        if 'commit_and_changeset' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit', kwargs={'id': changeset.id}))
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit_revision',
          kwargs={'id': character_order_revision.story_revision.id,
                  'model_name': 'story'}))

    except ViewTerminationError as vte:
        return vte.response




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

##############################################################################
# Mentoring
##############################################################################


@permission_required('indexer.can_contact')
def contacting(request):
    users = User.objects.filter(indexer__opt_in_email=True) \
                           .filter(is_active=True) \
                           .order_by('-date_joined') \
                           .select_related('indexer__country')

    return oi_render(
      request, 'oi/queues/contacting.html',
      {
        'users': users,
      })


@permission_required('indexer.can_mentor')
def mentoring(request):
    max_show_new = 50
    new_indexers = User.objects.filter(indexer__mentor=None) \
                       .filter(indexer__is_new=True) \
                       .filter(is_active=True) \
                       .order_by('-date_joined') \
                       .select_related('indexer__country')[:max_show_new]
    my_mentees = User.objects.filter(indexer__mentor=request.user) \
                             .filter(indexer__is_new=True) \
                             .select_related('indexer__country')
    mentees = User.objects.exclude(indexer__mentor=None) \
                          .filter(indexer__is_new=True) \
                          .exclude(indexer__mentor=request.user) \
                          .order_by('date_joined') \
                          .select_related('indexer__mentor__indexer',
                                          'indexer__country')

    return oi_render(
      request, 'oi/queues/mentoring.html',
      {
        'new_indexers': new_indexers,
        'my_mentees': my_mentees,
        'mentees': mentees,
        'max_show_new': max_show_new,
        'queue_name': 'mentoring',
      })


@permission_required('indexer.can_reserve')
def add_award(request):
    return add_generic(request, 'award')


@permission_required('indexer.can_reserve')
def add_creator_award(request, creator_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    creator = get_object_or_404(Creator, id=creator_id, deleted=False)

    if creator.pending_deletion():
        return render_error(request, 'Cannot add Award for '
                                     'creator "%s" since the record is '
                                     'pending deletion.' % creator)

    if request.method == 'GET':
        award_form = ReceivedAwardRevisionForm()

    elif request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
                    'show_creator', kwargs={'creator_id': creator_id}))

        award_form = ReceivedAwardRevisionForm(
                request.POST or None,
                request.FILES or None,
        )
        if award_form.is_valid():
            changeset = Changeset(indexer=request.user, state=states.OPEN,
                                  change_type=CTYPES['received_award'])
            changeset.save()
            revision = award_form.save(commit=False)
            revision.save_added_revision(
              changeset=changeset,
              recipient=creator,
              award=award_form.cleaned_data['award'])
            revision.save()

            process_data_source(award_form, '', changeset,
                                sourced_revision=revision)

            return submit(request, changeset.id)

    context = {'form': award_form,
               'object_name': 'Award of a Creator',
               'object_url': urlresolvers.reverse('add_creator_award',
                                                  kwargs={'creator_id':
                                                          creator_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


@permission_required('indexer.can_reserve')
def add_received_award(request, award_id, model_name, id):
    award = get_object_or_404(Award, id=award_id)

    if award.pending_deletion():
        return render_error(request, 'Cannot add to Award "%s" since the '
                                     'record is pending deletion.' % award)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse('show_award',
                                    kwargs={'award_id': award_id}))

    form = get_received_award_revision_form(user=request.user)(request.POST
                                                               or None)

    if model_name == 'story':
        selected_object = get_object_or_404(Story, id=id)
    elif model_name == 'issue':
        selected_object = get_object_or_404(Issue, id=id)
    elif model_name == 'series':
        selected_object = get_object_or_404(Series, id=id)
    else:
        raise NotImplementedError

    if form.is_valid():
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['received_award'])
        changeset.save()
        revision = form.save(commit=False)
        revision.save_added_revision(changeset=changeset,
                                     recipient=selected_object,
                                     award=award)
        revision.save()

        process_data_source(form, '', changeset,
                            sourced_revision=revision)

        return submit(request, changeset.id)

    extra_adding_info = 'the Award: %s for %s: %s' % (award,
                                                      model_name.capitalize(),
                                                      selected_object)

    return oi_render(
      request,
      'oi/edit/add_frame.html',
      {'action_label': 'Submit new received award',
       'form': form,
       'extra_adding_info': extra_adding_info,
       'object_url': urlresolvers.reverse('add_received_award',
                                          kwargs={'award_id': award.id,
                                                  'model_name': model_name,
                                                  'id': selected_object.id}),
       })


@permission_required('indexer.can_reserve')
def process_award_recipient(request, data, object_type, selected_id):
    if request.method != 'POST':
        return _cant_get(request)
    if 'cancel' in request.POST:
        return HttpResponseRedirect(
          urlresolvers.reverse('show_award',
                               kwargs={'id': data['award_id']}))

    return HttpResponseRedirect(
      urlresolvers.reverse('add_received_award',
                           kwargs={'award_id': data['award_id'],
                                   'model_name': object_type,
                                   'id': selected_id}))


@permission_required('indexer.can_reserve')
def select_award_recipient(request, award_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    award = get_object_or_404(Award, id=award_id)
    heading = 'Select recipient for an %s award' % (esc(award))

    data = {'award_id': award_id,
            'story': True,
            'issue': True,
            'series': True,
            'heading': mark_safe('<h2>%s</h2>' % heading),
            'target': 'a story, issue, or series',
            'return': 'process_award_recipient',
            'cancel': urlresolvers.reverse('show_award',
                                           kwargs={'award_id': award_id})}
    select_key = store_select_data(request, None, data)
    return HttpResponseRedirect(urlresolvers.reverse('select_object',
                                kwargs={'select_key': select_key}))


@permission_required('indexer.can_reserve')
def add_creator(request):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(reverse('add'))

    creator_form = get_creator_revision_form(user=request.user)(request.POST
                                                                or None)
    form_class = get_date_revision_form(user=request.user,
                                        date_help_links=CREATOR_HELP_LINKS)
    birth_date_form = form_class(request.POST or None, prefix='birth_date')
    death_date_form = form_class(request.POST or None, prefix='death_date')

    creator_names_formset = CreatorRevisionFormSet(request.POST or None)
    external_link_formset = ExternalLinkRevisionFormSet(request.POST or None)

    if not creator_form.is_valid() or not creator_names_formset.is_valid()\
       or not birth_date_form.is_valid() or not death_date_form.is_valid()\
       or not external_link_formset.is_valid():
        birth_date_form.fields['date'].label = 'Birth date'
        death_date_form.fields['date'].label = 'Death date'

        context = {'form': creator_form,
                   'creator_names_formset': creator_names_formset,
                   'birth_date_form': birth_date_form,
                   'death_date_form': death_date_form,
                   'external_link_formset': external_link_formset,
                   'object_name': 'Creator',
                   'object_url': urlresolvers.reverse('add_creator'),
                   'action_label': 'Submit new',
                   'mode': 'new',
                   'settings': settings}
        return oi_render(request, 'oi/edit/add_frame.html', context)

    changeset = Changeset(indexer=request.user, state=states.OPEN,
                          change_type=CTYPES['creator'])
    changeset.save()
    revision = creator_form.save(commit=False)
    revision.save_added_revision(changeset=changeset)
    revision.gcd_official_name = "Dummy"
    extra_forms = {'creator_names_formset': creator_names_formset,
                   'birth_date_form': birth_date_form,
                   'death_date_form': death_date_form,
                   'external_link_formset': external_link_formset
                   }
    revision.process_extra_forms(extra_forms)

    for field in _get_creator_sourced_fields():
        process_data_source(creator_form, field, revision.changeset,
                            sourced_revision=revision)
    return submit(request, changeset.id)


@permission_required('indexer.can_reserve')
def add_creator_signature(request, creator_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    creator = get_object_or_404(Creator, id=creator_id, deleted=False)

    if creator.pending_deletion():
        return render_error(request, 'Cannot add a Signature for '
                                     'creator "%s" since the record is '
                                     'pending deletion.' % creator)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
            'show_creator', kwargs={'creator_id': creator_id}))

    signature_form = CreatorSignatureRevisionForm(request.POST or None,
                                                  request.FILES or None)

    if signature_form.is_valid():
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['creator_signature'])
        changeset.save()

        revision = signature_form.save(commit=False)
        revision.save_added_revision(changeset=changeset, creator=creator)
        revision.save()
        if revision.image_revision:
            revision.image_revision.changeset = changeset
            revision.image_revision.object_id = revision.id
            revision.image_revision.content_type = ContentType\
                                   .objects.get_for_model(revision)
            revision.image_revision.save()

        process_data_source(signature_form, '', changeset,
                            sourced_revision=revision)
        return submit(request, changeset.id)

    context = {'form': signature_form,
               'object_name': 'Signature of a Creator',
               'object_url': urlresolvers.reverse('add_creator_signature',
                                                  kwargs={'creator_id':
                                                          creator_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


@permission_required('indexer.can_reserve')
def add_creator_relation(request, creator_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    creator = get_object_or_404(Creator, id=creator_id, deleted=False)

    if creator.pending_deletion():
        return render_error(request, 'Cannot add Relation for '
                                     'creator "%s" since the record is '
                                     'pending deletion.' % creator)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
                'show_creator', kwargs={'creator_id': creator_id}))

    initial = {}
    initial['from_creator'] = CreatorNameDetail.objects.get(
      creator__id=creator.id, is_official_name=True, deleted=False).id

    relation_form = CreatorRelationRevisionForm(request.POST or None,
                                                initial=initial)

    if relation_form.is_valid():
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['creator_relation'])
        changeset.save()

        revision = relation_form.save(commit=False)
        revision.save_added_revision(changeset=changeset, creator=creator)
        relation_form.save_m2m()
        revision.save()

        process_data_source(relation_form, '', changeset,
                            sourced_revision=revision)

        return submit(request, changeset.id)

    context = {'form': relation_form,
               'object_name': 'Relation with Creator',
               'object_url': urlresolvers.reverse('add_creator_relation',
                                                  kwargs={'creator_id':
                                                          creator_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


@permission_required('indexer.can_reserve')
def add_creator_school(request, creator_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    creator = get_object_or_404(Creator, id=creator_id, deleted=False)

    if creator.pending_deletion():
        return render_error(request, 'Cannot add School for '
                                     'creator "%s" since the record is '
                                     'pending deletion.' % creator)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
                'show_creator', kwargs={'creator_id': creator_id}))

    school_form = CreatorSchoolRevisionForm(request.POST or None)

    if school_form.is_valid():
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['creator_school'])
        changeset.save()

        revision = school_form.save(commit=False)
        revision.save_added_revision(changeset=changeset, creator=creator)
        revision.save()

        process_data_source(school_form, '', changeset,
                            sourced_revision=revision)

        return submit(request, changeset.id)

    context = {'form': school_form,
               'object_name': 'School of a Creator',
               'object_url': urlresolvers.reverse('add_creator_school',
                                                  kwargs={'creator_id':
                                                          creator_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


@permission_required('indexer.can_reserve')
def add_creator_degree(request, creator_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    creator = get_object_or_404(Creator, id=creator_id, deleted=False)

    if creator.pending_deletion():
        return render_error(request, 'Cannot add School Degree for '
                                     'creator "%s" since the record is '
                                     'pending deletion.' % creator)

    if request.method == 'POST' and 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
                'show_creator', kwargs={'creator_id': creator_id}))

    degree_form = CreatorDegreeRevisionForm(request.POST or None)

    if degree_form.is_valid():
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['creator_degree'])
        changeset.save()

        revision = degree_form.save(commit=False)
        revision.save_added_revision(changeset=changeset, creator=creator)
        revision.save()

        process_data_source(degree_form, '', changeset,
                            sourced_revision=revision)

        return submit(request, changeset.id)

    context = {'form': degree_form,
               'object_name': 'School Degree of a Creator',
               'object_url': urlresolvers.reverse('add_creator_degree',
                                                  kwargs={'creator_id':
                                                          creator_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


@permission_required('indexer.can_reserve')
def add_creator_membership(request, creator_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    creator = get_object_or_404(Creator, id=creator_id, deleted=False)

    if creator.pending_deletion():
        return render_error(request, 'Cannot add Membership '
                                     'creators since "%s" is deleted or '
                                     'pending deletion.' % creator)

    if request.method == 'GET':
        membership_form = CreatorMembershipRevisionForm()

    elif request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
                    'show_creator', kwargs={'creator_id': creator_id}))

        membership_form = CreatorMembershipRevisionForm(
                request.POST or None,
                request.FILES or None,
        )
        if membership_form.is_valid():
            changeset = Changeset(indexer=request.user, state=states.OPEN,
                                  change_type=CTYPES['creator_membership'])
            changeset.save()

            revision = membership_form.save(commit=False)

            revision.save_added_revision(changeset=changeset, creator=creator)
            revision.save()

            process_data_source(membership_form, '', changeset,
                                sourced_revision=revision)

            return submit(request, changeset.id)

    context = {'form': membership_form,
               'object_name': 'Membership of a Creator',
               'object_url': urlresolvers.reverse('add_creator_membership',
                                                  kwargs={'creator_id':
                                                          creator_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


@permission_required('indexer.can_reserve')
def add_creator_art_influence(request, creator_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    creator = get_object_or_404(Creator, id=creator_id, deleted=False)

    if creator.pending_deletion():
        return render_error(request, 'Cannot add Art Influence for '
                                     'creator "%s" since the record is '
                                     'pending deletion.' % creator)

    if request.method == 'GET':
        artinfluence_form = CreatorArtInfluenceRevisionForm()

    elif request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
                    'show_creator', kwargs={'creator_id': creator_id}))

        artinfluence_form = CreatorArtInfluenceRevisionForm(
                request.POST or None,
                request.FILES or None,
        )
        if artinfluence_form.is_valid():
            changeset = Changeset(indexer=request.user, state=states.OPEN,
                                  change_type=CTYPES['creator_art_influence'])
            changeset.save()

            revision = artinfluence_form.save(commit=False)

            revision.save_added_revision(changeset=changeset, creator=creator)
            revision.save()

            process_data_source(artinfluence_form, '', changeset,
                                sourced_revision=revision)
            return submit(request, changeset.id)

    context = {'form': artinfluence_form,
               'object_name': 'Art Influence of a Creator',
               'object_url': urlresolvers.reverse('add_creator_art_influence',
                                                  kwargs={'creator_id':
                                                          creator_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


@permission_required('indexer.can_reserve')
def add_creator_non_comic_work(request, creator_id):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    creator = get_object_or_404(Creator, id=creator_id, deleted=False)

    creator = Creator.objects.get(id=creator_id)
    if creator.deleted or creator.pending_deletion():
        return render_error(request, 'Cannot add NonComicWork '
                                     'creators since "%s" is deleted or '
                                     'pending deletion.' % creator)

    if request.method == 'GET':
        noncomicwork_form = CreatorNonComicWorkRevisionForm()

    elif request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
                    'show_creator',
                    kwargs={'creator_id': creator_id}))

        noncomicwork_form = CreatorNonComicWorkRevisionForm(
                request.POST or None,
                request.FILES or None,
        )
        if noncomicwork_form.is_valid():
            changeset = Changeset(indexer=request.user, state=states.OPEN,
                                  change_type=CTYPES['creator_non_comic_work'])
            changeset.save()

            revision = noncomicwork_form.save(commit=False)

            revision.save_added_revision(changeset=changeset, creator=creator)
            revision.save()

            process_data_source(noncomicwork_form, '', changeset,
                                sourced_revision=revision)
            return submit(request, changeset.id)

    context = {'form': noncomicwork_form,
               'object_name': 'Non Comic Work of a Creator',
               'object_url': urlresolvers.reverse('add_creator_non_comic_work',
                                                  kwargs={'creator_id':
                                                          creator_id}),
               'action_label': 'Submit new',
               'settings': settings}
    return oi_render(request, 'oi/edit/add_frame.html', context)


@permission_required('indexer.can_reserve')
def migrate_story_revision(request, id):
    story = get_object_or_404(StoryRevision, id=id)
    if request.user != story.changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may migrate stories.')

    if request.method != 'POST':
        return _cant_get(request)

    if story.old_credits():
        story.migrate_credits()

    if story.feature:
        story.migrate_feature()

    return HttpResponseRedirect(
      urlresolvers.reverse('edit_revision', kwargs={'model_name': 'story',
                                                    'id': story.id}))


@permission_required('indexer.can_reserve')
def migrate_issue_revision(request, id):
    issue = get_object_or_404(IssueRevision, id=id)
    if request.user != issue.changeset.indexer:
        return render_error(
          request, 'Only the reservation holder may migrate issues.')

    if request.method != 'POST':
        return _cant_get(request)

    if issue.editing:
        issue.migrate_credits()

    return HttpResponseRedirect(
      urlresolvers.reverse('edit_revision', kwargs={'model_name': 'issue',
                                                    'id': issue.id}))
