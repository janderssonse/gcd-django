"""Publisher/brand/printer add views (roadmap C1). Shared changeset-workflow helpers come from apps.oi.views.core; re-exported through the package __init__ so the historical import surface (oi_views.add_publisher, ...) is unchanged."""

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
def add_publisher(request):
    return add_generic(request, 'publisher')

@permission_required('indexer.can_reserve')
def add_indicia_publisher(request, parent_id):
    parent = get_object_or_404(Publisher, id=parent_id)
    if parent.deleted or parent.pending_deletion():
        return render_error(
          request,
          'Cannot add indicia / colophon publishers since '
          '"%s" is deleted or pending deletion.' % parent)
    save_kwargs = {'parent': parent}
    cancel = urlresolvers.reverse('show_publisher',
                                  kwargs={'publisher_id': parent_id})
    object_url = urlresolvers.reverse('add_indicia_publisher',
                                      kwargs={'parent_id': parent.id})
    return add_generic(
      request, 'indicia_publisher',
      object_url=object_url,
      object_name='Indicia / Colophon Publisher',
      cancel=cancel,
      save_kwargs=save_kwargs)

@permission_required('indexer.can_reserve')
def add_brand_group(request, parent_id):
    parent = get_object_or_404(Publisher, id=parent_id)
    if parent.deleted or parent.pending_deletion():
        return render_error(
          request,
          'Cannot add brands since '
          '"%s" is deleted or pending deletion.' % parent)
    save_kwargs = {'parent': parent}
    cancel = urlresolvers.reverse('show_publisher',
                                  kwargs={'publisher_id': parent_id})
    object_url = urlresolvers.reverse('add_brand_group',
                                      kwargs={'parent_id': parent.id})
    return add_generic(
      request, 'brand_group',
      object_url=object_url,
      object_name='Brand Group',
      cancel=cancel,
      save_kwargs=save_kwargs)

@permission_required('indexer.can_reserve')
def add_brand(request, brand_group_id=None, publisher_id=None):
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    if brand_group_id is not None:
        try:
            brand_group = BrandGroup.objects.get(id=brand_group_id)
            if brand_group.deleted or brand_group.pending_deletion():
                return render_error(
                  request, 'Cannot add brands '
                  'since "%s" is deleted or pending deletion.' % brand_group)
        except (BrandGroup.DoesNotExist, BrandGroup.MultipleObjectsReturned):
            return render_error(
              request, 'Could not find Brand Group for id %d' % brand_group_id)
        publisher = None
    else:
        try:
            publisher = Publisher.objects.get(id=publisher_id)
            if publisher.deleted or publisher.pending_deletion():
                return render_error(
                  request, 'Cannot add brands '
                  'since "%s" is deleted or pending deletion.' % publisher)
        except (Publisher.DoesNotExist, Publisher.MultipleObjectsReturned):
            return render_error(
              request, 'Could not find Publisher for id %d' % publisher_id)
        brand_group = None

    if request.method != 'POST':
        form = get_brand_revision_form(user=request.user, publisher=publisher,
                                       brand_group=brand_group)()
        return _display_add_brand_form(request, form, brand_group, publisher)

    if 'cancel' in request.POST:
        if brand_group_id:
            return HttpResponseRedirect(urlresolvers.reverse(
                'show_brand_group',
                kwargs={'brand_group_id': brand_group_id}))
        else:
            return HttpResponseRedirect(urlresolvers.reverse(
                'show_publisher',
                kwargs={'publisher_id': publisher_id}))

    form = get_brand_revision_form(user=request.user, publisher=publisher,
                                   brand_group=brand_group)(request.POST,
                                                            request.FILES)
    if not form.is_valid():
        return _display_add_brand_form(request, form, brand_group, publisher)

    changeset = Changeset(indexer=request.user, state=states.OPEN,
                          change_type=CTYPES['brand'])
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

def _display_add_brand_form(request, form, brand_group=None, publisher=None):
    object_name = 'Brand Emblem'
    if brand_group:
        object_url = urlresolvers.reverse('add_brand_via_group',
                                          kwargs={'brand_group_id':
                                                  brand_group.id})
    else:
        object_url = urlresolvers.reverse(
          'add_brand_via_publisher', kwargs={'publisher_id': publisher.id})

    return oi_render(
      request, 'oi/edit/add_frame.html',
      {
        'object_name': object_name,
        'object_url': object_url,
        'action_label': 'Submit new',
        'form': form,
      })

@permission_required('indexer.can_reserve')
def add_brand_use(request, brand_id, publisher_id=None):
    brand = get_object_or_404(Brand, id=brand_id, deleted=False)
    if brand.pending_deletion():
        return render_error(
          request, 'Cannot add a brand use '
          'since "%s" is pending deletion.' % brand)
    if publisher_id:
        publisher = get_object_or_404(Publisher, id=publisher_id,
                                      deleted=False)
        if publisher.pending_deletion():
            return render_error(
              request, 'Cannot add a brand use '
              'since "%s" is pending deletion.' % publisher)
        if request.method != 'POST':
            # we should only get here by a POST
            raise NotImplementedError

        if 'cancel' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
                'show_brand',
                kwargs={'brand_id': brand_id}))

        form = get_brand_use_revision_form(user=request.user)(request.POST)
        if not form.is_valid:
            return _display_add_brand_use_form(request, form, brand, publisher)

        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES['brand_use'])
        changeset.save()
        revision = form.save(commit=False)
        revision.save_added_revision(changeset=changeset, emblem=brand,
                                     publisher=publisher)
        return submit(request, changeset.id)
    else:
        data = {'heading': mark_safe('<h2>Select Publisher where the Brand %s '
                                     'was in use</h2>' % esc(brand.name)),
                'target': 'a publisher',
                'brand_id': brand_id,
                'publisher': True,
                'return': 'process_add_brand_use',
                'cancel': urlresolvers.reverse('show_brand',
                                               kwargs={'brand_id': brand_id})}
        select_key = store_select_data(request, None, data)
        return HttpResponseRedirect(urlresolvers.reverse(
          'select_object', kwargs={'select_key': select_key}))

@permission_required('indexer.can_reserve')
def process_add_brand_use(request, data, object_type, publisher_id):
    if object_type != 'publisher':
        raise ValueError
    brand = get_object_or_404(Brand, id=data['brand_id'], deleted=False)

    publisher = get_object_or_404(Publisher, id=publisher_id, deleted=False)

    form = get_brand_use_revision_form(user=request.user)
    return _display_add_brand_use_form(request, form, brand, publisher)

def _display_add_brand_use_form(request, form, brand, publisher):
    object_name = 'BrandUse for %s at %s' % (brand, publisher)
    object_url = urlresolvers.reverse('add_brand_use',
                                      kwargs={'brand_id': brand.id,
                                              'publisher_id': publisher.id})

    return oi_render(
      request, 'oi/edit/add_frame.html',
      {
        'object_name': object_name,
        'object_url': object_url,
        'action_label': 'Submit new',
        'form': form,
      })

@permission_required('indexer.can_reserve')
def add_printer(request):
    return add_generic(request, 'printer')

@permission_required('indexer.can_reserve')
def add_indicia_printer(request, parent_id):
    parent = get_object_or_404(Printer, id=parent_id)
    if parent.deleted or parent.pending_deletion():
        return render_error(
          request,
          'Cannot add indicia printers since '
          '"%s" is deleted or pending deletion.' % parent)
    save_kwargs = {'parent': parent}
    cancel = urlresolvers.reverse('show_printer',
                                  kwargs={'printer_id': parent_id})
    object_url = urlresolvers.reverse('add_indicia_printer',
                                      kwargs={'parent_id': parent.id})
    return add_generic(request, 'indicia_printer',
                       object_url=object_url,
                       object_name='Indicia Printer',
                       cancel=cancel,
                       save_kwargs=save_kwargs)
