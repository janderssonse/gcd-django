"""Award add views (roadmap C1): award, creator-award, and received-award adds plus their recipient-select helpers. Shared changeset-workflow helpers come from apps.oi.views.core; re-exported through the package __init__ so the historical import surface is unchanged."""

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


