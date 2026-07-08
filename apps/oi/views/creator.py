"""Creator add views (roadmap C1): creator plus signature, relation, school, degree, membership, art-influence and non-comic-work sub-adds. Shared changeset-workflow helpers come from apps.oi.views.core; re-exported through the package __init__ so the historical import surface is unchanged."""

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


