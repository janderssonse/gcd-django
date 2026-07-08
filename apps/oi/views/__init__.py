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

# issue views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.issue import (  # noqa: F401
    _clean_bulk_issue_change_form, edit_issues_in_bulk, _display_bulk_issue_change_form, init_added_variant,
    add_issue, add_variant_to_issue_revision, add_variant_issuerevision, add_variant_issue,
    _display_add_issue_form, add_issues, _build_whole_numbered_issues, _build_per_volume_issues,
    _build_per_year_issues, _build_per_year_volume_issues, _build_issue, _display_bulk_issue_form,
    compare_issues_copy, move_issue, migrate_issue_revision)

# series views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.series import (  # noqa: F401
    add_series, _display_add_series_form, edit_series_bonds, save_selected_series_bond,
    edit_series_bond, save_added_series_bond, add_series_bond, move_series,
    reorder_series, reorder_series_by_key_date, reorder_series_by_issue_number, _reorder_series)

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

# queue/compare/preview views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.queue import (  # noqa: F401
    _revision_accessor, show_queue, ChangesetTypeFilter, show_approved,
    show_commented, show_editor_log, show_cover_queue, compare,
    get_cover_width, cover_compare, image_compare, preview)

# creator views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.creator import (  # noqa: F401
    add_creator, add_creator_signature, add_creator_relation,
    add_creator_school, add_creator_degree, add_creator_membership,
    add_creator_art_influence, add_creator_non_comic_work)

# award views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.award import (  # noqa: F401
    add_award, add_creator_award, add_received_award,
    process_award_recipient, select_award_recipient)

# feature views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.feature import (  # noqa: F401
    add_feature, add_feature_logo, add_feature_relation)

# character views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.character import (  # noqa: F401
    add_universe, add_character, add_character_relation, add_group,
    add_group_relation, add_group_membership, add_group_member)

# mentoring views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.mentoring import (  # noqa: F401
    contacting, mentoring)

# ongoing views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.ongoing import (  # noqa: F401
    ongoing, delete_ongoing)

# cover views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.cover import (  # noqa: F401
    move_cover, undo_move_cover)

# reprint views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.reprint import (  # noqa: F401
    parse_reprint, list_issue_reprints, reserve_reprint, edit_reprint,
    add_reprint, select_internal_object, _selected_copy_sequence,
    copy_sequence, create_matching_sequence, confirm_reprint, save_reprint,
    remove_reprint_revision)

##############################################################################
# Bulk Changes
##############################################################################







##############################################################################
# Adding Items
##############################################################################
























































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












##############################################################################
# Moving Items
##############################################################################






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


##############################################################################
# Reordering
##############################################################################












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
# Mentoring
##############################################################################


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


