"""Issue add/variant/bulk/move views (roadmap C1). Shared changeset-workflow helpers come from apps.oi.views.core; re-exported through the package __init__ so the historical import surface is unchanged."""

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
