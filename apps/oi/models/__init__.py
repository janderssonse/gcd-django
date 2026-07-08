# -*- coding: utf-8 -*-
import itertools
import operator
import re
import calendar
import os
import glob
from datetime import timedelta

from django import forms
from django.conf import settings
from django.db import models, transaction, IntegrityError
from django.db.models import F, Manager
from django.db.models.fields import Field, related
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, \
                                               GenericRelation
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as esc
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError, FieldDoesNotExist

from imagekit.cachefiles.backends import CacheFileState
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from taggit.managers import TaggableManager

from apps.oi import states, relpath

from apps.stddata.models import Country, Language, Date, Script
from apps.stats.models import RecentIndexedIssue, CountStats

from apps.gcd.models import (
    Publisher, IndiciaPublisher, BrandGroup, Brand, BrandUse, Series,
    SeriesBond, Cover, Image, Issue, IssueCredit, PublisherCodeNumber,
    CodeNumberType, Story, StoryCredit, StoryCharacter, CharacterRole,
    StoryGroup, StoryArc, StoryArcRelation, Universe, Multiverse,
    CharacterOrderType, CharacterOrder,
    BiblioEntry, Reprint,
    SeriesPublicationType, SeriesBondType, StoryType, CreditType, FeatureType,
    Feature, FeatureLogo, FeatureRelation, Character, CharacterRelation,
    CharacterNameDetail, Group, GroupNameDetail, GroupRelation,
    GroupMembership, ImageType, Printer, IndiciaPrinter,
    Creator, CreatorArtInfluence, CreatorDegree, CreatorMembership,
    CreatorNameDetail, CreatorNonComicWork, CreatorSchool, CreatorRelation,
    CreatorSignature, NonComicWorkYear, Award, ReceivedAward, DataSource,
    ExternalLink, STORY_TYPES, CREDIT_TYPES, VCS_Codes)

from apps.gcd.models.gcddata import GcdData, GcdLink

from apps.gcd.models.issue import issue_descriptor
from apps.gcd.models.story import show_feature, show_feature_as_text, \
                                  show_characters, show_title, \
                                  _get_civilian_identity
from apps.gcd.models.image import CropToFace
from apps.indexer.views import ErrorWithMessage

from functools import reduce

# Base revision layer (roadmap C1). Re-exported here so the historical import
# surface (from apps.oi.models import Revision, Changeset, CTYPES, ...) is
# unchanged and so the concrete entity revisions below can reference it.
from apps.oi.models.base import (  # noqa: F401
    ChangeType, CTYPES, CTYPES_INLINE, CTYPES_BULK,
    ACTION_ADD, ACTION_DELETE, ACTION_MODIFY,
    IMP_BONUS_ADD, IMP_COVER_VALUE, IMP_IMAGE_VALUE,
    IMP_APPROVER_VALUE, IMP_DELETE,
    update_count, set_series_first_last, validated_isbn,
    remove_leading_article, on_sale_date_as_string, on_sale_date_fields,
    get_keywords, save_keywords, _check_year, _imps_for_years,
    _get_revision_lock, _free_revision_lock,
    _removed_related_objects, _process_formset,
    Changeset, ChangesetComment, RevisionLock, RevisionManager,
    RevisionQuerySet, Revision, OngoingReservation, ExternalLinkRevision)

# publisher cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.publisher import (  # noqa: F401
    PublisherRevisionBase, PublisherRevision, IndiciaPublisherRevision,
    BrandGroupRevision, BrandRevision, PreviewBrand,
    get_brand_use_field_list, BrandUseRevision, PrinterRevision,
    IndiciaPrinterRevision)

# cover cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.cover import (  # noqa: F401
    CoverRevisionManager, CoverRevision)

# series cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.series import (  # noqa: F401
    get_series_field_list, SeriesRevision, SeriesBondRevisionManager,
    get_series_bond_field_list, SeriesBondRevision)

# issue cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.issue import (  # noqa: F401
    get_issue_field_list, PublisherCodeNumberRevision, IssueCreditRevision,
    IssueRevision, PreviewIssue)

# story cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.story import (  # noqa: F401
    get_story_field_list, StoryCreditRevision, StoryCharacterRevision,
    CharacterOrderRevision, CharacterThroughOrderRevision, StoryGroupRevision,
    StoryArcRevision, StoryArcRelationRevision, _order_civilian_after_alias,
    StoryRevision, PreviewStory, BiblioEntryRevision)

# feature cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.feature import (  # noqa: F401
    FeatureRevision, FeatureLogoRevision, FeatureRelationRevision)

# character cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.character import (  # noqa: F401
    UniverseRevision, PreviewUniverse, CharacterGroupRevisionBase,
    CharacterRevision, PreviewCharacter, CharacterNameDetailRevision,
    CharacterRelationRevision, GroupRevision, GroupNameDetailRevision,
    GroupRelationRevision, GroupMembershipRevision)

# reprint cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.reprint import (  # noqa: F401
    get_reprint_field_list, ReprintRevision)

# image cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.image import (  # noqa: F401
    ImageRevisionManager, _clear_image_cache, ImageRevision)

# award cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.award import (  # noqa: F401
    AwardRevision, ReceivedAwardRevision, PreviewReceivedAward)

# datasource cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.datasource import (  # noqa: F401
    DataSourceRevisionManager, DataSourceRevision, process_data_source,
    reserve_data_sources)

# creator cluster (roadmap C1), re-exported for the stable import surface.
from apps.oi.models.creator import (  # noqa: F401
    _get_creator_sourced_fields, get_creator_field_list, CreatorRevision,
    PreviewCreator, CreatorRelationRevision, CreatorNameDetailRevision,
    CreatorSignatureRevision, CreatorSchoolRevision, PreviewCreatorSchool,
    CreatorDegreeRevision, PreviewCreatorDegree, CreatorMembershipRevision,
    PreviewCreatorMembership, CreatorArtInfluenceRevision, PreviewCreatorArtInfluence,
    MultiURLValidator, CreatorNonComicWorkRevision, PreviewCreatorNonComicWork)

LANGUAGE_STATS = ['de']

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


# #########################################################################
# Revision-definition validation (roadmap B0). Field identity in the revision
# system is name strings matched to model attributes at runtime, so a rename
# silently turns a lookup into a no-op -- the brand_emblem class of bug. The
# validators now live in a submodule (first step of the C1 split); re-export
# them so `from apps.oi.models import validate_*` keeps working.
from apps.oi.models.validation import (  # noqa: E402
    validate_revision_definitions,
    validate_revision_field_lists,
    _concrete_revision_classes,
    _walk_field_path,
    _revision_attr_exists,
)
