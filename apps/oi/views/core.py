"""Changeset-workflow core for the OI views (roadmap C1): the REVISION_CLASSES/DISPLAY_CLASSES maps and the reserve/edit/submit/approve/discard lifecycle plus shared helpers every entity view builds on."""

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


REVISION_CLASSES = {
    'publisher': PublisherRevision,
    'indicia_publisher': IndiciaPublisherRevision,
    'brand_group': BrandGroupRevision,
    'brand': BrandRevision,
    'brand_emblem': BrandRevision,
    'brand_use': BrandUseRevision,
    'printer': PrinterRevision,
    'indicia_printer': IndiciaPrinterRevision,
    'series': SeriesRevision,
    'series_bond': SeriesBondRevision,
    'issue': IssueRevision,
    'story': StoryRevision,
    'biblio_entry': BiblioEntryRevision,
    'character_order': CharacterOrderRevision,
    'story_arc': StoryArcRevision,
    'story_arc_relation': StoryArcRelationRevision,
    'feature': FeatureRevision,
    'feature_logo': FeatureLogoRevision,
    'feature_relation': FeatureRelationRevision,
    'universe': UniverseRevision,
    'character': CharacterRevision,
    'character_relation': CharacterRelationRevision,
    'group': GroupRevision,
    'group_relation': GroupRelationRevision,
    'group_membership': GroupMembershipRevision,
    'cover': CoverRevision,
    'reprint': ReprintRevision,
    'image': ImageRevision,
    'award': AwardRevision,
    'received_award': ReceivedAwardRevision,
    'creator': CreatorRevision,
    'creator_signature': CreatorSignatureRevision,
    'creator_art_influence': CreatorArtInfluenceRevision,
    'creator_degree': CreatorDegreeRevision,
    'creator_membership': CreatorMembershipRevision,
    'creator_non_comic_work': CreatorNonComicWorkRevision,
    'creator_relation': CreatorRelationRevision,
    'creator_school': CreatorSchoolRevision,
}

# naming convention: xxx_yyy_zzz <-> XxxYyyZzz
DISPLAY_CLASSES = {
    'publisher': Publisher,
    'indicia_publisher': IndiciaPublisher,
    'brand_group': BrandGroup,
    'brand': Brand,
    'brand_emblem': Brand,
    'brand_use': BrandUse,
    'printer': Printer,
    'indicia_printer': IndiciaPrinter,
    'series': Series,
    'series_bond': SeriesBond,
    'issue': Issue,
    'story': Story,
    'biblio_entry': BiblioEntry,
    'story_arc': StoryArc,
    'story_arc_relation': StoryArcRelation,
    'feature': Feature,
    'feature_logo': FeatureLogo,
    'feature_relation': FeatureRelation,
    'universe': Universe,
    'character': Character,
    'character_relation': CharacterRelation,
    'group': Group,
    'group_relation': GroupRelation,
    'group_membership': GroupMembership,
    'cover': Cover,
    'reprint': Reprint,
    'image': Image,
    'award': Award,
    'received_award': ReceivedAward,
    'creator': Creator,
    'creator_signature': CreatorSignature,
    'creator_art_influence': CreatorArtInfluence,
    'creator_degree': CreatorDegree,
    'creator_membership': CreatorMembership,
    'creator_non_comic_work': CreatorNonComicWork,
    'creator_relation': CreatorRelation,
    'creator_school': CreatorSchool,
}

REACHED_CHANGE_LIMIT = 'You have reached your limit of open changes.  You ' \
  'must submit or discard some changes from your edit queue before you ' \
  'can edit any more.  If you are a new user this number is very low ' \
  'but will be increased as your first changes are approved. ' \
  'If you are an experienced indexer and frequently hit ' \
  'your reservation limit please contact us.'

##############################################################################
# Helper functions
##############################################################################


def _cant_get(request):
    return render_error(
      request,
      'This page may only be accessed through the proper form.',
      redirect=False)


def oi_render(request, template_name, context={}):
    context['EDITING'] = True
    return render(request, template_name, context)

##############################################################################
# Generic view functions
##############################################################################


@permission_required('indexer.can_reserve')
def delete(request, id, model_name):
    display_obj = get_object_or_404(DISPLAY_CLASSES[model_name], id=id)
    if request.method == 'GET':

        # These can only be reached if people try to paste in URLs directly,
        # but as we know, some people do that sort of thing.
        if getattr(display_obj, 'deleted', False):
            return render_error(
              request,
              'Cannot delete "%s" as it is already deleted.' % display_obj,
              redirect=False)
        if not display_obj.deletable():
            return render_error(
              request,
              '"%s" cannot be deleted.' % display_obj, redirect=False)

        return oi_render(
          request,
          'oi/edit/deletion_comment.html',
          {
            'model_name': model_name,
            'id': id,
            'object': display_obj,
            'no_comment': False
          })

    if 'cancel' in request.POST:
        if model_name == 'cover':
            return HttpResponseRedirect(urlresolvers.reverse('edit_covers',
                                        kwargs={'issue_id':
                                                display_obj.issue.id}))
        if model_name == 'series_bond':
            return HttpResponseRedirect(urlresolvers.reverse('show_series',
                                        kwargs={'series_id':
                                                display_obj.origin_id}))
        return HttpResponseRedirect(
          urlresolvers.reverse('show_%s' % model_name,
                               kwargs={'%s_id' % model_name: id}))

    if not request.POST.__contains__('comments') or \
       request.POST['comments'].strip() == '':
        return oi_render(
          request,
          'oi/edit/deletion_comment.html',
          {
            'model_name': model_name,
            'id': id,
            'object': display_obj,
            'no_comment': True
          })

    return reserve(request, id, model_name, delete=True)


@permission_required('indexer.can_reserve')
def reserve(request, id, model_name, delete=False,
            callback=None, callback_args=None):
    if request.method != 'POST':
        return _cant_get(request)
    display_obj = get_object_or_404(DISPLAY_CLASSES[model_name], id=id)

    if getattr(display_obj, 'deleted', False):
        if model_name == 'cover':
            return HttpResponseRedirect(
              urlresolvers.reverse('show_issue',
                                   kwargs={'issue_id': display_obj.issue.id}))
        return HttpResponseRedirect(
          urlresolvers.reverse('change_history',
                               kwargs={'model_name': model_name, 'id': id}))

    try:  # if something goes wrong we unreserve
        if delete:
            # TODO, this likely should not be needed anymore with the new
            # transaction handling ?
            # In case someone else deleted while page was open or if it is not
            # deletable because of other actions in the interim (adding to an
            # issue for brand/ind_pub, modifying covers for issue, etc.)
            if not display_obj.deletable():
                # Technically nothing to roll back, but keep this here in case
                # someone adds more code later.
                return render_error(
                  request, 'This object fails the requirements for deletion.')

            changeset = _do_reserve(request.user, display_obj, model_name,
                                    delete=True)
        else:
            changeset = _do_reserve(request.user, display_obj, model_name)

        if changeset is False:
            return render_error(request, REACHED_CHANGE_LIMIT)
        if changeset is None:
            return render_error(
              request,
              'Cannot edit "%s" as it is reserved, or data objects required'
              ' for its editing are reserved.' % display_obj)

        if delete:
            changeset.submit(notes=request.POST['comments'], delete=True)
            if model_name in ['image', 'series_bond']:
                return HttpResponseRedirect(urlresolvers.reverse('editing'))
            if model_name == 'cover':
                return HttpResponseRedirect(urlresolvers.reverse(
                  'edit_covers',
                  kwargs={'issue_id': display_obj.issue.id}))
            if model_name == 'brand_use':
                return HttpResponseRedirect(urlresolvers.reverse(
                     'show_brand',
                     kwargs={'brand_id': display_obj.emblem.id}))
            return HttpResponseRedirect(urlresolvers.reverse(
                     'show_%s' % model_name,
                     kwargs={str('%s_id' % model_name): id}))
        else:
            if callback:
                if not callback(changeset, display_obj, **callback_args):
                    _free_revision_lock(display_obj)
                    changeset.delete()
                    return render_error(
                      request, 'Not all objects could be reserved.')
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit', kwargs={'id': changeset.id}))

    except ValueError:
        # _free_revision_lock(display_obj)
        raise


def _do_reserve(indexer, display_obj, model_name, delete=False,
                changeset=None):
    """
    The creation of the revision and if needed changeset happens here.
    Returns either the changeset, False (when indexer cannot reserve more)
    or None (when something goes wrong). The revision_lock is deleted for
    both False and None as return values.
    """
    if model_name != 'cover' and (delete is False or indexer.indexer.is_new)\
       and indexer.indexer.can_reserve_another() is False:
        return False

    revision_lock = _get_revision_lock(display_obj)
    if not revision_lock:
        return None

    if delete:
        # Deletions are submitted immediately which will set the correct state.
        new_state = states.UNRESERVED
    else:
        comment = ''
        new_state = states.OPEN

    if not changeset:
        changeset_created = True
        changeset = Changeset(indexer=indexer, state=new_state,
                              change_type=CTYPES[model_name])
        changeset.save()

        if not delete:
            # Deletions are immediately submitted, which will add the
            # appropriate initial comment- no need to add two.
            changeset.comments.create(commenter=indexer,
                                      text=comment,
                                      old_state=states.UNRESERVED,
                                      new_state=changeset.state)
    else:
        changeset_created = False

    revision_lock.changeset = changeset
    revision_lock.save()

    # TODO clone_revision is deprecated
    if hasattr(REVISION_CLASSES[model_name].objects, 'clone_revision'):
        revision = REVISION_CLASSES[model_name].objects.clone_revision(
          display_obj, changeset=changeset)
    else:
        revision = REVISION_CLASSES[model_name].clone(display_obj,
                                                      changeset=changeset)

    if delete:
        revision.deleted = True
        revision.save()

    try:
        with transaction.atomic():
            revision._create_dependent_revisions(delete=delete)
    except IntegrityError:
        _free_revision_lock(revision.source)
        if changeset_created:
            changeset.delete()
        return None

    return changeset


@permission_required('indexer.can_reserve')
def edit_two_issues(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, deleted=False)
    if is_locked(issue):
        return render_error(request, 'Issue %s is reserved.' % issue,
                            redirect=False)
    data = {'issue_id': issue_id,
            'issue': True,
            'heading': mark_safe('<h2>Select issue to edit with %s</h2>'
                                 % esc(issue.full_name())),
            'target': 'an issue',
            'return': 'confirm_two_edits',
            'cancel': urlresolvers.reverse('show_issue',
                                           kwargs={'issue_id': issue_id})}
    select_key = store_select_data(request, None, data)
    return HttpResponseRedirect(urlresolvers.reverse(
      'select_object', kwargs={'select_key': select_key}))


@permission_required('indexer.can_reserve')
def confirm_two_edits(request, data, object_type, issue_two_id):
    if object_type != 'issue':
        raise ValueError
    issue_one = get_object_or_404(Issue, id=data['issue_id'], deleted=False)
    if is_locked(issue_one):
        return render_error(request, 'Issue %s is reserved.' % issue_one,
                            redirect=False)

    issue_two = get_object_or_404(Issue, id=issue_two_id, deleted=False)
    if is_locked(issue_two):
        return render_error(request, 'Issue %s is reserved.' % issue_two,
                            redirect=False)
    return oi_render(
      request, 'oi/edit/confirm_two_edits.html',
      {'issue_one': issue_one, 'issue_two': issue_two})


@permission_required('indexer.can_reserve')
# in case of variants: issue_one = variant, issue_two = base
def reserve_two_issues(request, issue_one_id, issue_two_id):
    if request.method != 'POST':
        return _cant_get(request)
    if 'cancel' in request.POST:
        return HttpResponseRedirect(urlresolvers.reverse(
          'show_issue', kwargs={'issue_id': issue_one_id}))
    issue_one = get_object_or_404(Issue, id=issue_one_id, deleted=False)

    kwargs = {'issue_one': issue_one}
    return reserve(request, issue_two_id, 'issue',
                   callback=reserve_other_issue,
                   callback_args=kwargs)


def reserve_other_issue(changeset, revision, issue_one):
    if not _do_reserve(changeset.indexer, issue_one, 'issue',
                       changeset=changeset):
        return False
    changeset.change_type = CTYPES['two_issues']
    changeset.save()
    return True


@permission_required('indexer.can_reserve')
def edit_revision(request, id, model_name):
    revision = get_object_or_404(REVISION_CLASSES[model_name], id=id)
    form_class = get_revision_form(revision, user=request.user)
    form = form_class(instance=revision)
    extra_forms = revision.extra_forms(request)
    return _display_edit_form(request, revision.changeset, form, revision,
                              extra_forms)


@permission_required('indexer.can_reserve')
def edit(request, id):
    changeset = get_object_or_404(Changeset, id=id)

    if changeset.inline():
        revision = changeset.inline_revision()
        form_class = get_revision_form(revision, user=request.user)
        form = form_class(instance=revision)
        extra_forms = revision.extra_forms(request)
    else:
        form = None
        revision = None
        extra_forms = None
    # Note that for non-inline changesets, no form is expected so
    # it may be None.
    return _display_edit_form(request, changeset, form, revision, extra_forms)


def _display_edit_form(request, changeset, form, revision=None,
                       extra_forms=None):
    if revision is None or changeset.inline():
        template = 'oi/edit/changeset.html'
        if revision is None:
            revision = changeset.inline_revision()
    else:
        template = 'oi/edit/revision.html'

    context_vars = {
        'changeset': changeset,
        'revision': revision,
        'form': form,
        'states': states,
        'settings': settings,
        'CTYPES': CTYPES
    }
    if extra_forms:
        context_vars.update(extra_forms)
    response = oi_render(request, template, context_vars)
    response['Cache-Control'] = "no-cache, no-store," \
                                " max-age=0, must-revalidate"
    return response


@permission_required('indexer.can_reserve')
def submit(request, id):
    """
    Submit a change and go to the reservations queue.
    """
    if request.method != 'POST':
        return _cant_get(request)

    changeset = get_object_or_404(Changeset, id=id)
    if (request.user != changeset.indexer):
        return oi_render(
          request, 'indexer/error.html',
          {'error_text': 'A change may only be submitted by its author.'})
    comment_text = request.POST['comments'].strip()
    if comment_text == '' and changeset.approver is None and \
       changeset.comments.count() == 1:
        changeset.calculate_imps()
        if changeset.imps == 0 and not \
           changeset.characterorderrevisions.exists():
            return oi_render(
              request, 'indexer/error.html',
              {'error_text': mark_safe('A submission needs to consists of at '
                                       'least one change to the data or have '
                                       'a comment. <a href="%s">Go back.</a>'
                                       % request.META['HTTP_REFERER'])
               })

    changeset.submit(notes=comment_text)
    if changeset.approver is not None:
        if comment_text:
            comment = 'The submission includes the comment:\n"%s"' % \
                      comment_text
        else:
            comment = ''
        email_body = """
Hello from the %s!


  You have a change for "%s" by %s to review. %s

Please go to %s to compare the changes.

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
                     str(changeset),
                     str(changeset.indexer.indexer),
                     comment,
                     settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
                       'compare', kwargs={'id': changeset.id}),
                     settings.SITE_NAME,
                     settings.SITE_URL)

        changeset.approver.email_user('GCD change to review', email_body,
                                      settings.EMAIL_INDEXING)

    if comment_text:
        send_comment_observer(request, changeset, comment_text)

    # If there are only CharacterOrderRevisions, and no actual changes,
    # we can skip the reviewing and commit.
    if changeset.imps == 0 and changeset.characterorderrevisions.exists():
        is_changed = False
        for c in changeset.revisions:
            c.compare_changes()
            if c.is_changed and type(c) is not CharacterOrderRevision:
                is_changed = True
                break
        if not is_changed:
            changeset.approver = User.objects.get(username='anon')
            changeset.state = states.REVIEWING
            changeset.approve('Auto-approved since there are only character '
                              'order changes.')

    return HttpResponseRedirect(urlresolvers.reverse('editing'))


def show_error_with_return(request, text, changeset):
    return render_error(
      request, '%s <a href="%s">Return to changeset.</a>'
      % (esc(text), urlresolvers.reverse('edit',
                                         kwargs={'id': changeset.id})),
      is_safe=True)


def _save_data_source_revision(form, revision, field):
    data_source_revision = revision.changeset\
        .datasourcerevisions.filter(field=field)
    if data_source_revision:
        # TODO support more than one revision
        data_source_revision = data_source_revision[0]
    process_data_source(form, field, revision.changeset,
                        revision=data_source_revision,
                        sourced_revision=revision)


def _extra_forms_valid(request, extra_forms):
    is_valid = True
    for form in extra_forms:
        if extra_forms[form]:  # some forms are sometimes None
            is_valid = is_valid and extra_forms[form].is_valid()
    return is_valid


def _save(request, form, revision, changeset=None, model_name=None):
    extra_forms = revision.extra_forms(request)
    if form.is_valid() and _extra_forms_valid(request, extra_forms):
        revision = form.save(commit=False)
        changeset = revision.changeset
        if 'comments' in form.cleaned_data and 'submit' not in request.POST:
            comments = form.cleaned_data['comments']
            if comments is not None and comments != '':
                revision.comments.create(commenter=request.user,
                                         changeset=changeset,
                                         text=comments,
                                         old_state=changeset.state,
                                         new_state=changeset.state)

        revision.save()
        revision.process_extra_forms(extra_forms)
        if revision.changeset.change_type == CTYPES['series'] and \
           'move_to_publisher_with_id' in form.cleaned_data and \
           request.user.has_perm('indexer.can_approve') and \
           form.cleaned_data['move_to_publisher_with_id']:
            try:
                publisher_id = form.cleaned_data['move_to_publisher_with_id']
                publisher = Publisher.objects.get(id=publisher_id,
                                                  deleted=False)
            except Publisher.DoesNotExist:
                return show_error_with_return(
                  request,
                  'No publisher with id %d.' % publisher_id, changeset)
            if publisher.pending_deletion():
                return show_error_with_return(
                  request, 'Publisher %s is '
                  'pending deletion' % str(publisher), changeset)
            if revision.changeset.issuerevisions.count() == 0:
                revision.series.active_issues()
                if RevisionLock.objects.filter(
                  object_id__in=revision.series.active_issues()
                                               .values_list('id', flat=True),
                  content_type=ContentType.objects.get(model='Issue')
                ).exists():
                    return show_error_with_return(
                      request,
                      ('Some issues for series %s are reserved. '
                       'No move possible.') % revision.series,
                      changeset)
            return HttpResponseRedirect(urlresolvers.reverse(
              'move_series', kwargs={'series_revision_id': revision.id,
                                     'publisher_id': publisher_id}))

        if hasattr(form, 'save_m2m'):
            # TODO handle sources in standard workflow
            # I don't quite understand what is going on here, but for image
            # and cover revision form.save_m2m() fails with a comment.
            # But we don't need form.save_m2m() for these anyway. I suspect
            # problems since relation to ChangesetComment is called 'comments'
            # and the text 'field' is called that as well.
            if not (len(form.cleaned_data) == 1 and
               'comments' in form.cleaned_data):
                if revision.changeset.change_type in [
                                        CTYPES['received_award'],
                                        CTYPES['creator_art_influence'],
                                        CTYPES['creator_degree'],
                                        CTYPES['creator_membership'],
                                        CTYPES['creator_non_comic_work'],
                                        CTYPES['creator_relation'],
                                        CTYPES['creator_school'],
                                        CTYPES['creator_signature']]:
                    _save_data_source_revision(form, revision, '')
                    if revision.changeset.change_type == \
                       CTYPES['creator_relation']:
                        form.save_m2m()
                elif revision.changeset.change_type == CTYPES['creator']:
                    for field in _get_creator_sourced_fields():
                        data_source_revision = revision.changeset \
                            .datasourcerevisions.filter(field=field)
                        if data_source_revision:
                            # TODO support more than one revision
                            data_source_revision = data_source_revision[0]
                        process_data_source(form, field, revision.changeset,
                                            revision=data_source_revision,
                                            sourced_revision=revision)
                else:
                    form.save_m2m()

        revision.post_form_save()

        if 'submit' in request.POST:
            return submit(request, revision.changeset.id)
        if 'queue' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse('editing'))
        if 'save' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit_revision',
              kwargs={'model_name': model_name, 'id': revision.id}))
        if 'save_migrate' in request.POST:
            if model_name == 'issue':
                if revision.editing:
                    revision.migrate_credits()
            else:
                if revision.old_credits():
                    revision.migrate_credits()
                if revision.feature:
                    revision.migrate_feature()
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit_revision',
              kwargs={'model_name': model_name, 'id': revision.id}))
        if 'save_migrate_feature' in request.POST:
            if revision.feature:
                revision.migrate_feature()
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit_revision',
              kwargs={'model_name': model_name, 'id': revision.id}))
        if 'create_appearance_order' in request.POST and model_name == 'story':
            return HttpResponseRedirect(urlresolvers.reverse(
              'create_character_order_revision',
              kwargs={'story_revision_id': revision.id, 'type_id': 1}))
        if 'edit_appearance_order' in request.POST and model_name == 'story':
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit_character_order_revision',
              kwargs={'story_revision_id': revision.id, 'type_id': 1}))
        if 'create_importance_order' in request.POST and model_name == 'story':
            return HttpResponseRedirect(urlresolvers.reverse(
              'create_character_order_revision',
              kwargs={'story_revision_id': revision.id, 'type_id': 2}))
        if 'edit_importance_order' in request.POST and model_name == 'story':
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit_character_order_revision',
              kwargs={'story_revision_id': revision.id, 'type_id': 2}))
        if 'save_and_set_universe' in request.POST:
            if revision.universe.count() == 1:
                characters = revision.story_character_revisions.filter(
                  universe=None,
                  deleted=False)
                for character in characters:
                    character.universe = revision.universe.get()
                    character.save()
                groups = revision.story_group_revisions.filter(
                  universe=None,
                  deleted=False)
                for group in groups:
                    group.universe = revision.universe.get()
                    group.save()
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit_revision',
              kwargs={'model_name': model_name, 'id': revision.id}))
        if 'save_return' in request.POST:
            # BiblioEntry needs second form for specific fields
            if revision.source_class == Story \
              and revision.type.id == STORY_TYPES['about comics']:
                if hasattr(revision, 'biblioentryrevision'):
                    biblio_revision = revision.biblioentryrevision
                else:
                    biblio_revision = BiblioEntryRevision(
                      storyrevision_ptr=revision)
                    biblio_revision.__dict__.update(revision.__dict__)
                    biblio_revision.save()
                return HttpResponseRedirect(
                  urlresolvers.reverse('edit_revision',
                                       kwargs={'model_name': 'biblio_entry',
                                               'id': biblio_revision.id}))
            return HttpResponseRedirect(urlresolvers.reverse(
              'edit',
              kwargs={'id': revision.changeset.id}))
        return render_error(
          request,
          'Revision saved but cannot determine which '
          'page to load now.  Contact an editor if this error persists.')

    if changeset is None:
        changeset = revision.changeset
    revision.extra_forms_errors(request, form, extra_forms)
    return _display_edit_form(request, changeset, form, revision,
                              extra_forms=extra_forms)


@permission_required('indexer.can_reserve')
def retract(request, id):
    """
    Retract a pending change back into your reserved queue.
    """
    if request.method != 'POST':
        return _cant_get(request)
    changeset = get_object_or_404(Changeset.objects.select_for_update(), id=id)

    if request.user != changeset.indexer:
        return oi_render(
          request, 'indexer/error.html',
          {'error_text': 'A change may only be retracted by its author.'})
    comment_text = request.POST['comments'].strip()
    changeset.retract(notes=comment_text)

    if comment_text:
        send_comment_observer(request, changeset, comment_text)

    return HttpResponseRedirect(
      urlresolvers.reverse('edit', kwargs={'id': changeset.id}))


@permission_required('indexer.can_reserve')
def confirm_discard(request, id, has_comment=0):
    """
    Indexer has to confirm the discard of a change.
    """
    changeset = get_object_or_404(Changeset.objects.select_for_update(), id=id)
    if request.user != changeset.indexer:
        return render_error(
          request,
          'Only the author of the changeset can access this page.',
          redirect=False)

    if changeset.state not in states.ACTIVE:
        return render_error(
          request, 'Only ACTIVE changes can be discarded.')

    if request.method != 'POST':
        return oi_render(request, 'oi/edit/confirm_discard.html',
                         {'changeset': changeset})

    if 'discard' in request.POST:
        if has_comment == '1' and changeset.approver:
            comment_text = changeset.comments.latest('created').text
            comment = 'The discard includes the comment:\n"%s"' % comment_text
        else:
            comment = ''
            comment_text = ''
        changeset.discard(discarder=request.user)
        if changeset.approver:
            email_body = """
Hello from the %s!


  The change for "%s" by %s which you were reviewing was discarded. %s

You can view the full change at %s.

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
                         str(changeset),
                         str(changeset.indexer.indexer),
                         comment,
                         settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
                           'compare', kwargs={'id': changeset.id}),
                         settings.SITE_NAME,
                         settings.SITE_URL)

            changeset.approver.email_user('Reviewed GCD change discarded',
                                          email_body, settings.EMAIL_INDEXING)
        if comment_text:
            send_comment_observer(request, changeset, comment_text)
        return HttpResponseRedirect(urlresolvers.reverse('editing'))
    else:
        # it would be nice if we would be able to go back the page
        # from where the 'discard' originated, but due to the
        # redirect we don't have this information here.
        return HttpResponseRedirect(urlresolvers.reverse('edit',
                                    kwargs={'id': changeset.id}))


@permission_required('indexer.can_reserve')
def discard(request, id):
    """
    Discard a change and go to the reservations queue.
    """
    if request.method != 'POST':
        return _cant_get(request)
    changeset = get_object_or_404(Changeset.objects.select_for_update(), id=id)

    if request.user != changeset.indexer and \
       request.user != changeset.approver:
        return oi_render(request, 'indexer/error.html',
                         {'error_text': 'Only the author or the assigned '
                                        'editor can discard a change.'})

    comment_text = request.POST['comments'].strip()
    if request.user != changeset.indexer and not comment_text:
        return render_error(request,
                            'You must explain why you are rejecting this '
                            'change.  Please press the "back" button and use '
                            'the comments field for the explanation.')

    # get a confirmation to avoid unwanted discards
    if request.user == changeset.indexer:
        if comment_text:
            changeset.comments.create(commenter=request.user,
                                      text=comment_text,
                                      old_state=changeset.state,
                                      new_state=changeset.state)
            has_comment = 1
        else:
            has_comment = 0
        return HttpResponseRedirect(urlresolvers.reverse('confirm_discard',
                                    kwargs={'id': changeset.id,
                                            'has_comment': has_comment}))

    changeset.discard(discarder=request.user, notes=comment_text)

    if request.user == changeset.approver:
        email_body = """
Hello from the %s!


  Your change for "%s" was rejected by GCD editor %s with the comment:
"%s"

You can view the full change at %s.

If you disagree please either contact the editor directly via the e-mail
%s or post a message on the main mailing-list
which is also reachable via http://groups.google.com/group/gcd-main.

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
                     str(changeset),
                     str(changeset.approver.indexer),
                     comment_text,
                     settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
                       'compare', kwargs={'id': changeset.id}),
                     changeset.approver.email,
                     settings.SITE_NAME,
                     settings.SITE_URL)

        changeset.indexer.email_user('GCD change rejected', email_body,
                                     settings.EMAIL_INDEXING)
        if comment_text:
            send_comment_observer(request, changeset, comment_text)
        if request.user.approved_changeset.filter(state=states.REVIEWING)\
                                          .count():
            return HttpResponseRedirect(urlresolvers.reverse('reviewing'))
        else:
            if changeset.change_type is CTYPES['cover']:
                return HttpResponseRedirect(
                  urlresolvers.reverse('pending_covers'))
            else:
                return HttpResponseRedirect(urlresolvers.reverse('pending'))


@permission_required('indexer.can_approve')
def assign(request, id):
    """
    Move a change into your approvals queue, and go to the queue.
    """
    if request.method != 'POST':
        return _cant_get(request)

    changeset = get_object_or_404(Changeset.objects.select_for_update(), id=id)
    if request.user == changeset.indexer:
        return render_error(request, 'You may not approve your own changes.')

    comment_text = request.POST['comments'].strip()
    # TODO: rework error checking strategy.  This is a hack for the most
    # common case but we probably shouldn't be doing this check in the
    # model layer in the first place.
    try:
        changeset.assign(approver=request.user, notes=comment_text)
    except ViewTerminationError:
        if changeset.approver is None:
            return render_error(
              request,
              'This change has been retracted by the indexer after you loaded '
              'the previous page. This results in you seeing an "Assign" '
              'button. Please use the back button to return to the '
              'Pending queue.',
              redirect=False)
        else:
            return render_error(
              request,
              ('This change is already being reviewed by %s who may have '
               'assigned it after you loaded the previous page.  '
               'This results in you seeing an '
               '"Assign" button even though the change is under review. '
               'Please use the back button to return to the Pending queue.') %
              changeset.approver.indexer,
              redirect=False)

    if changeset.indexer.indexer.is_new and \
       changeset.indexer.indexer.mentor is None and\
       changeset.change_type is not CTYPES['cover']:

        changeset.indexer.indexer.mentor = request.user
        changeset.indexer.indexer.save()

        for pending in changeset.indexer.changesets\
                                        .filter(state=states.PENDING):
            try:
                pending.assign(approver=request.user, notes='')
            except ValueError:
                # Someone is already reviewing this.
                # Unlikely, and just let it go.
                pass

    if comment_text:
        email_body = """
Hello from the %s!


  %s became editor of the change "%s" with the comment:
"%s"

You can view the full change at %s.

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
                     str(request.user.indexer),
                     str(changeset),
                     comment_text,
                     settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
                       'compare', kwargs={'id': changeset.id}),
                     settings.SITE_NAME,
                     settings.SITE_URL)
        changeset.indexer.email_user('GCD comment', email_body,
                                     settings.EMAIL_INDEXING)

        send_comment_observer(request, changeset, comment_text)

    if changeset.approver.indexer.collapse_compare_view:
        option = '?collapse=1'
    else:
        option = ''
    return HttpResponseRedirect(urlresolvers.reverse(
                                'compare', kwargs={'id': changeset.id})
                                + option)


@permission_required('indexer.can_approve')
def release(request, id):
    """
    Move a change out of your approvals queue, and go back to your queue.
    """
    if request.method != 'POST':
        return _cant_get(request)

    changeset = get_object_or_404(Changeset.objects.select_for_update(), id=id)
    if request.user != changeset.approver:
        return oi_render(
          request, 'indexer/error.html',
          {'error_text': 'A change may only be released by its approver.'})

    comment_text = request.POST['comments'].strip()
    changeset.release(notes=comment_text)
    if comment_text:
        email_body = """
Hello from the %s!


  editor %s released the change "%s" with the comment:
"%s"

You can view the full change at %s.

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
                     str(request.user.indexer),
                     str(changeset),
                     comment_text,
                     settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
                       'compare', kwargs={'id': changeset.id}),
                     settings.SITE_NAME,
                     settings.SITE_URL)
        changeset.indexer.email_user(
          'GCD comment', email_body, settings.EMAIL_INDEXING)

        send_comment_observer(request, changeset, comment_text)

    if request.user.approved_changeset.filter(state=states.REVIEWING).count():
        return HttpResponseRedirect(urlresolvers.reverse('reviewing'))
    else:
        if changeset.change_type is CTYPES['cover']:
            return HttpResponseRedirect(urlresolvers.reverse('pending_covers'))
        else:
            return HttpResponseRedirect(urlresolvers.reverse('pending'))


def discuss(request, id):
    """
    Move a change into the discussion state and go back to your queue.
    """
    if request.method != 'POST':
        return _cant_get(request)

    changeset = get_object_or_404(Changeset.objects.select_for_update(), id=id)
    if request.user != changeset.approver and \
       request.user != changeset.indexer:
        return oi_render(
          request, 'indexer/error.html',
          {'error_text': 'A change may only be put into discussion by its '
                         'indexer or approver.'})
    if request.user == changeset.approver and \
       changeset.state != states.REVIEWING:
        return render_error(
          request, 'Only REVIEWING changes can be put into discussion.')
    if request.user == changeset.indexer and \
       changeset.state not in [states.OPEN, states.REVIEWING]:
        return render_error(
          request,
          'Only EDITING OR REVIEWING changes can be put into discussion.')

    comment_text = request.POST['comments'].strip()
    changeset.discuss(commenter=request.user, notes=comment_text)

    if comment_text:
        email_comments = ' with the comment:\n"%s"' % comment_text
    else:
        email_comments = '.'

    if request.user == changeset.indexer:
        action_by = 'indexer %s' % str(changeset.indexer.indexer)
        start_comment = 'The reviewed'
    else:
        action_by = 'editor %s' % str(changeset.approver.indexer)
        start_comment = 'Your'

    email_body = """
Hello from the %s!


  %s change for "%s" was put into the discussion state by GCD %s%s

You can view the full change at %s.

thanks,
-the %s team

%s
""" % (settings.SITE_NAME,
       start_comment,
       str(changeset),
       action_by,
       email_comments,
       settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
         'compare', kwargs={'id': changeset.id}),
       settings.SITE_NAME,
       settings.SITE_URL)

    if comment_text:
        subject = 'GCD change put into discussion with a comment'
        send_comment_observer(request, changeset, comment_text)
    else:
        subject = 'GCD change put into discussion'

    if request.user == changeset.indexer:
        changeset.approver.email_user(subject, email_body,
                                      settings.EMAIL_INDEXING)
        return HttpResponseRedirect(urlresolvers.reverse('editing'))
    else:
        changeset.indexer.email_user(subject, email_body,
                                     settings.EMAIL_INDEXING)

        if request.user.approved_changeset.filter(
          state=states.REVIEWING).count():
            return HttpResponseRedirect(urlresolvers.reverse('reviewing'))
        else:
            if changeset.change_type is CTYPES['cover']:
                return HttpResponseRedirect(
                  urlresolvers.reverse('pending_covers'))
            else:
                return HttpResponseRedirect(urlresolvers.reverse('pending'))


def _reserve_newly_created_issue(issue, changeset, indexer):
    new_change = _do_reserve(indexer, issue, 'issue')
    # TODO maybe check for False vs. None here ?
    if not new_change:
        _send_declined_reservation_email(indexer, issue)


@permission_required('indexer.can_approve')
def approve(request, id):

    """
    Approve a change and return to your approvals queue.
    """
    if request.method != 'POST':
        return _cant_get(request)

    changeset = get_object_or_404(Changeset.objects.select_for_update(), id=id)
    if request.user != changeset.approver:
        return render_error(
          request, 'A change may only be approved by its approver.')

    if changeset.state not in [states.DISCUSSED, states.REVIEWING] \
       or changeset.approver is None:
        return render_error(
          request, 'Only REVIEWING changes with an approver can be approved.')

    comment_text = request.POST['comments'].strip()
    changeset.approve(notes=comment_text)
    email_comments = '.'
    postscript = ''
    if comment_text:
        email_comments = ' with the comment:\n"%s"' % comment_text
    else:
        postscript = """
PS: You can change your email settings on your profile page:
%s
Currently, your profile is set to receive emails about change approvals even
if the approver did not comment.  To turn these off, just edit your profile
and uncheck the "Approval emails" box.
""" % (settings.SITE_URL.rstrip('/') + urlresolvers.reverse('default_profile'))

    if changeset.indexer.indexer.notify_on_approve or comment_text:
        email_body = """
Hello from the %s!


  Your change for "%s" was approved by GCD editor %s%s

You can view the full change at %s.

thanks,
-the %s team

%s
%s
""" % (settings.SITE_NAME,
                     str(changeset),
                     str(changeset.approver.indexer),
                     email_comments,
                     settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
                       'compare', kwargs={'id': changeset.id}),
                     settings.SITE_NAME,
                     settings.SITE_URL,
                     postscript)

        if comment_text:
            subject = 'GCD change approved with a comment'
            send_comment_observer(request, changeset, comment_text)
        else:
            subject = 'GCD change approved'
        changeset.indexer.email_user(subject, email_body,
                                     settings.EMAIL_INDEXING)

    # Note that series ongoing reservations must be processed first, as
    # they could potentially apply to the issue reservations if we ever
    # implement complex changesets.
    # TODO does this belong into model.py ?
    for series_revision in \
        changeset.seriesrevisions.filter(deleted=False,
                                         reservation_requested=True,
                                         series__created__gt=F('created'),
                                         series__is_current=True,
                                         series__ongoing_reservation=None,
                                         is_singleton=False):
        if (changeset.indexer.ongoing_reservations.count() >=
           changeset.indexer.indexer.max_ongoing):
            _send_declined_ongoing_email(changeset.indexer,
                                         series_revision.series)

        ongoing = OngoingReservation(indexer=changeset.indexer,
                                     series=series_revision.series)
        ongoing.save()

    # here created_gte needed for singleton issues freshly created
    for issue_revision in \
        changeset.issuerevisions.filter(deleted=False,
                                        reservation_requested=True,
                                        issue__created__gte=F('created'),
                                        series__ongoing_reservation=None):
        _reserve_newly_created_issue(issue_revision.issue, changeset,
                                     changeset.indexer)

    for issue_revision in \
        changeset.issuerevisions.filter(
                                 deleted=False,
                                 reservation_requested=True,
                                 issue__created__gt=F('created'),
                                 series__ongoing_reservation__isnull=False,
                                 issue__variant_of__isnull=False):
        _reserve_newly_created_issue(issue_revision.issue, changeset,
                                     changeset.indexer)

    # here created_gt since for issues reserved by an ongoing reservation the
    # timestamps can be the same
    for issue_revision in \
        changeset.issuerevisions.filter(
                                 deleted=False,
                                 issue__created__gt=F('created'),
                                 series__ongoing_reservation__isnull=False,
                                 issue__variant_of=None):
        _reserve_newly_created_issue(
          issue_revision.issue, changeset,
          issue_revision.series.ongoing_reservation.indexer)

    # Move brand new indexers to probationary status on first approval.
    if changeset.change_type is not CTYPES['cover'] and \
       changeset.indexer.indexer.max_reservations == \
       settings.RESERVE_MAX_INITIAL:
        i = changeset.indexer.indexer
        i.max_reservations = settings.RESERVE_MAX_PROBATION
        i.max_ongoing = settings.RESERVE_MAX_ONGOING_PROBATION
        i.save()

    if request.user.approved_changeset.filter(state=states.REVIEWING).count():
        return HttpResponseRedirect(urlresolvers.reverse('reviewing'))
    else:
        # to avoid counting assume for now that cover queue is never empty
        if changeset.change_type is CTYPES['cover']:
            return HttpResponseRedirect(urlresolvers.reverse('pending_covers'))
        else:
            return HttpResponseRedirect(urlresolvers.reverse('pending'))


def _send_declined_reservation_email(indexer, issue):
    email_body = """
Hello from the %s!


  Your requested reservation of issue "%s" was declined because you have
reached your maximum number of open changes.  Please visit your editing
queue at %s%s and submit or discard some changes and then
try your edit again.

  Your maximum change limit starts low as a new user but is increased as
more of your changes are approved.

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
       issue,
       settings.SITE_URL,
       urlresolvers.reverse('editing'),
       settings.SITE_NAME, settings.SITE_URL)

    indexer.email_user(
      'GCD automatic reservation declined',
      email_body,
      settings.EMAIL_INDEXING)


def _send_declined_ongoing_email(indexer, series):
    course_of_action = ("Please contact a GCD Editor on the gcd_main group "
                        "(http://groups.google.com/group/gcd-main/) "
                        "if you would like to request a limit increase.")
    if indexer.indexer.is_new:
        course_of_action = ("As a new user you will gain the ability to hold "
                            "series revisions as your initial changes get "
                            "approved.")
    email_body = """
Hello from the %s!


  Your requested ongoing reservation of series "%s" was declined because
you have reached your maximum number of ongoing reservations.  %s

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
       series,
       course_of_action,
       settings.SITE_NAME, settings.SITE_URL)

    indexer.email_user(
      'GCD automatic reservation declined',
      email_body,
      settings.EMAIL_INDEXING)


@permission_required('indexer.can_approve')
def disapprove(request, id):
    """
    Disapprove a change and return to your approvals queue.
    """
    if request.method != 'POST':
        return _cant_get(request)

    changeset = get_object_or_404(Changeset.objects.select_for_update(), id=id)
    if request.user != changeset.approver:
        return render_error(
          request, 'A change may only be rejected by its approver.')

    comment_text = request.POST['comments'].strip()
    if not comment_text:
        return render_error(request,
                            'You must explain why you are disapproving this '
                            'change.  Please press the "back" button and use '
                            'the comments field for the explanation.')

    changeset.disapprove(notes=comment_text)

    email_body = """
Hello from the %s!


  Your change for "%s" was sent back by GCD editor %s with the comment:
"%s"

Please go to %s to re-edit or reply.

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
       str(changeset),
       str(changeset.approver.indexer),
       comment_text,
       settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
         'edit', kwargs={'id': changeset.id}),
       settings.SITE_NAME,
       settings.SITE_URL)

    changeset.indexer.email_user(
      'GCD change sent back', email_body, settings.EMAIL_INDEXING)

    send_comment_observer(request, changeset, comment_text)

    if request.user.approved_changeset.filter(state=states.REVIEWING).count():
        return HttpResponseRedirect(urlresolvers.reverse('reviewing'))
    else:
        if changeset.change_type is CTYPES['cover']:
            return HttpResponseRedirect(
                urlresolvers.reverse('pending_covers'))
        else:
            return HttpResponseRedirect(urlresolvers.reverse('pending'))


def send_comment_observer(request, changeset, comments):
    email_body = """
Hello from the %s!


  %s added a comment to the change "%s" to which you added a comment before:
"%s"

You can view the full change at %s.

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
       str(request.user.indexer),
       str(changeset),
       comments,
       settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
         'compare', kwargs={'id': changeset.id}),
       settings.SITE_NAME,
       settings.SITE_URL)

    if changeset.approver:
        excluding = [changeset.indexer, changeset.approver, request.user]
    else:
        excluding = [changeset.indexer, request.user]
    commenters = set(changeset.comments.exclude(text='')
                     .exclude(commenter__in=excluding)
                     .values_list('commenter', flat=True))
    for commenter in commenters:
        User.objects.get(id=commenter).email_user(
          'GCD comment', email_body, settings.EMAIL_INDEXING)


@permission_required('indexer.can_reserve')
def add_comments(request, id):
    """
    Comment on a change and return to the compare page.
    """
    if request.method != 'POST':
        return _cant_get(request)

    changeset = get_object_or_404(Changeset, id=id)
    comment_text = request.POST['comments'].strip()
    if comment_text:
        changeset.comments.create(commenter=request.user,
                                  text=comment_text,
                                  old_state=changeset.state,
                                  new_state=changeset.state)

        email_body = """
Hello from the %s!


  %s added a comment to the change "%s":
"%s"

You can view the full change at %s.

thanks,
-the %s team
%s
""" % (settings.SITE_NAME,
                     str(request.user.indexer),
                     str(changeset),
                     comment_text,
                     settings.SITE_URL.rstrip('/') + urlresolvers.reverse(
                       'compare', kwargs={'id': changeset.id}),
                     settings.SITE_NAME,
                     settings.SITE_URL)

        if request.user != changeset.indexer:
            changeset.indexer.email_user(
              'GCD comment', email_body, settings.EMAIL_INDEXING)
        if changeset.approver and request.user != changeset.approver:
            changeset.approver.email_user(
              'GCD comment', email_body, settings.EMAIL_INDEXING)

        send_comment_observer(request, changeset, comment_text)

    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    from apps.oi.views import compare
    return HttpResponseRedirect(urlresolvers.reverse(compare,
                                                     kwargs={'id': id}))


@permission_required('indexer.can_reserve')
def process(request, id):
    """
    Entry point for forms with multiple actions.

    This handles adding comments (with no state change) directly, and routes
    the request to other views for all other cases.
    """
    if request.method != 'POST':
        return _cant_get(request)

    if 'submit' in request.POST:
        changeset = get_object_or_404(Changeset, id=id)
        if changeset.inline():
            revision = changeset.inline_revision()
            form_class = get_revision_form(revision, user=request.user)
            form = form_class(request.POST, request.FILES, instance=revision)
            return _save(request, form, revision, changeset=changeset)
        else:
            return submit(request, id)

    if 'retract' in request.POST:
        return retract(request, id)

    if 'discard' in request.POST or 'cancel' in request.POST:
        return discard(request, id)

    if 'assign' in request.POST:
        return assign(request, id)

    if 'release' in request.POST:
        return release(request, id)

    if 'discuss' in request.POST:
        return discuss(request, id)

    if 'approve' in request.POST:
        return approve(request, id)

    if 'disapprove' in request.POST:
        return disapprove(request, id)

    if 'add_comment' in request.POST:
        return add_comments(request, id)

    return render_error(
      request, 'Unknown action requested!  Please try again. '
      'If this error message persists, please contact an Editor.')


@permission_required('indexer.can_reserve')
def process_revision(request, id, model_name):
    if request.method != 'POST':
        return _cant_get(request)

    if 'cancel_return' in request.POST:
        revision = get_object_or_404(REVISION_CLASSES[model_name], id=id)
        return HttpResponseRedirect(urlresolvers.reverse(
          'edit', kwargs={'id': revision.changeset.id}))

    if 'save' in request.POST or 'save_return' in request.POST \
       or 'save_migrate' in request.POST \
       or 'save_migrate_feature' in request.POST \
       or 'save_and_set_universe' in request.POST \
       or 'edit_appearance_order' in request.POST \
       or 'create_appearance_order' in request.POST \
       or 'edit_importance_order' in request.POST \
       or 'create_importance_order' in request.POST:
        revision = get_object_or_404(REVISION_CLASSES[model_name], id=id)
        form = get_revision_form(revision,
                                 user=request.user)(request.POST,
                                                    instance=revision)
        return _save(request, form, revision, model_name=model_name)

    return render_error(
      request,
      'Unknown action requested!  Please try again.  If this error message '
      'persists, please contact an Editor.')


@permission_required('indexer.can_reserve')
def add_generic(request, model_name,
                object_url='', object_name=None,
                initial={}, cancel='', save_kwargs={}):
    """
    Add a new object through the Online Indexer interface.

    This view handles the creation of new objects that do not have extra
    forms (such as publishers, features, etc.) through a revision/changeset
    workflow.

    It requires the user to have the 'indexer.can_reserve' permission and
    checks if the user can reserve another item.

    Args:
        request (HttpRequest): The HTTP request object.
        model_name (str): The name of the model being added (e.g.,
                          'publisher', 'feature').
        object_url (str, optional): The URL to redirect to for the form.
            Defaults to ''.
        object_name (str, optional): Display name for the object type.
            Defaults to None.
        initial (dict, optional): Initial data for the form. Defaults to {}.
        cancel (str, optional): URL to redirect to on cancel. Defaults to ''.
        save_kwargs (dict, optional): Additional keyword arguments to pass to
            the save_added_revision method. Defaults to {}.

    Returns:
        HttpResponse:
            - If user has reached change limit: error page
            - If form is cancelled: redirect to cancel URL or add page
            - If form is valid: redirect to submit page for the created
              changeset
            - If form is invalid or GET request: renders the add form template

    Notes:
        - Creates a new Changeset with OPEN state when form is valid
        - Uses get_revision_form to dynamically get the appropriate form
          class
        - Object name and URL are auto-generated if not provided
    """
    if not request.user.indexer.can_reserve_another():
        return render_error(request, REACHED_CHANGE_LIMIT)

    if request.method == 'POST' and 'cancel' in request.POST:
        if cancel:
            return HttpResponseRedirect(cancel)
        return HttpResponseRedirect(urlresolvers.reverse('add'))

    form = get_revision_form(model_name=model_name,
                             user=request.user)(request.POST or None,
                                                initial=initial)
    if form.is_valid():
        changeset = Changeset(indexer=request.user, state=states.OPEN,
                              change_type=CTYPES[model_name])
        changeset.save()
        revision = form.save(commit=False)
        revision.save_added_revision(changeset=changeset, **save_kwargs)
        return submit(request, changeset.id)
    else:
        if not object_name:
            object_name = DISPLAY_CLASSES[model_name].__name__
        if not object_url:
            object_url = urlresolvers.reverse('add_%s' % model_name)

        return oi_render(
          request, 'oi/edit/add_frame.html',
          {
            'object_name': object_name,
            'object_url': object_url,
            'action_label': 'Submit New',
            'form': form,
          })


def _process_reorder_form(request, parent, sort_field, child_name,
                          child_class):
    """
    Pull out the order fields and process the child objects in a generic way.
    """

    reorder_map = {}
    reorder_list = []
    sort_code_set = set()
    input_regexp = re.compile(r'%s_(?P<%s_id>\d+)$' % (sort_field, child_name))
    child_group = '%s_id' % child_name

    for input in request.POST:
        m = input_regexp.match(input)
        if m:
            child_id = int(m.group(child_group))
            try:
                sort_code = float(request.POST[input])
            except ValueError:
                raise ViewTerminationError(render_error(
                  request, "%s must be a number", redirect=False))

            if sort_code in sort_code_set:
                raise ViewTerminationError(render_error(
                  request,
                  "Cannot have duplicate %ss: %f" % (sort_field, sort_code),
                  redirect=False))

            sort_code_set.add(sort_code)

            reorder_map[child_id] = sort_code
            reorder_list.append(child_id)

    def _compare_sort_input(a, b):
        diff = reorder_map[a] - reorder_map[b]
        if diff > 0:
            return 1
        if diff < 0:
            return -1
        return 0

    reorder_list.sort(key=lambda b: reorder_map[b])

    # Use in_bulk to ensure the specific issue order
    child_map = child_class.objects.in_bulk(reorder_list)
    return [child_map[child_id] for child_id in reorder_list]


def _reorder_children(request, parent, children, sort_field, child_set,
                      commit, unique=True, skip=None, extras=None):
    """
    Internal function implementing reordering in a generic way.
    Note that "children" may be a list or a query_set, while "child_set"
    must be the query set as accessed through the parent object.
    This may be accessed in a non-standard way, which is why it must be
    passed separately.

    The "skip" parameter is new revision for which a gap should be left.
    If there is already a revision with this sequence number, then the gap
    must go before that revision.  The new revision's sort code should
    be updated if necessary for it to fit into the gap properly.
    """

    # TODO:  Ideally we would have a mixin class, reorderable, that would
    #        implement this, and all reorderables could be assumed to have
    #        a sort_code field and a get_children method instead of all of
    #        this getattr/setattr madness.  This is something we should look
    #        into once the more urgent features are complete.  Our design
    #        is far too procedural in this area.

    if unique:
        # There's a "unique together" constraint on series_id and sort_code in
        # the issue table, which is great for avoiding nonsensical sort_code
        # situations that we had in the old system, but annoying when updating
        # the codes.  Get around it by shifting the numbers down to starting
        # at one if they'll fit, or up above the current range if not.  Given
        # that the numbers were all set to consecutive ranges when we migrated
        # to this system, and this code always produces consecutive ranges, the
        # chances that we won't have room at one end or the other are very
        # slight.

        # Use child_set because children may be a list, not a query set.
        min = child_set.aggregate(Min(sort_field))['%s__min' % sort_field]
        max = child_set.aggregate(Max(sort_field))['%s__max' % sort_field]
        num_children = child_set.count()

        if num_children < min:
            current_code = 1
        elif num_children <= sys.maxsize - max:
            current_code = max + 1
        else:
            # This should be extremely rare, so let's not bother to
            # code our way out.
            raise ViewTerminationError(render_error(
              request,
              "Can't find room for rearranged sort codes, please contact "
              "an admin",
              redirect=False))
    else:
        # If there's no uniqueness constraints, always sort starting with zero.
        current_code = 0

    child_list = []
    found_skip = False
    for child in children:
        if skip is not None:
            skip_code = getattr(skip, sort_field)
            if not found_skip and current_code >= skip_code:
                found_skip = True
                setattr(skip, sort_field, current_code)
                current_code += 1
        if commit:
            setattr(child, sort_field, current_code)
            child.save()
        else:
            child_list.append((child, current_code))
        current_code += 1

    # special case if there were no children and therefore for loop did nothing
    if not children and skip is not None:
        setattr(skip, sort_field, current_code)

    if commit and extras:
        for child in extras:
            setattr(child, sort_field, current_code)
            child.save()
            current_code += 1

    return child_list
