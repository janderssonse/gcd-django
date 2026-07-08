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


# story views (roadmap C1), re-exported for the stable import surface.
from apps.oi.views.story import (  # noqa: F401
    add_story_arc, add_story_arc_relation, add_story,
    _get_initial_add_story_data, copy_story_revision, story_select_compare,
    compare_stories_copy, edit_character_order_revision,
    create_character_order_revision, move_story_revision,
    remove_story_revision, toggle_delete_story_revision, reorder_stories,
    reorder_characters, migrate_story_revision)
