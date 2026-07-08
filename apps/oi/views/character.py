"""Character, group and universe add views (roadmap C1): universe, character and character-relation adds plus group, group-relation, group-membership and group-member adds. Shared changeset-workflow helpers come from apps.oi.views.core; re-exported through the package __init__ so the historical import surface is unchanged."""

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


