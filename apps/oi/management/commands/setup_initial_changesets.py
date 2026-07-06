"""
Create approved changesets for existing display objects.

Data dumps from comics.org do not include the change history, so
objects imported from a dump cannot be edited: the OI expects every
object to have at least one committed revision. This command creates
an automatically generated, approved changeset per object so that a
development database built from a dump supports editing.

Adapted from setup_initial_changesets.py in the retired
gcd-django-docker repository.
"""

from django.core.management.base import BaseCommand

from apps.gcd.models import Issue
from apps.indexer.models import User
from apps.oi import states
from apps.oi.models import Changeset, IssueCreditRevision, \
                           StoryRevision, StoryCreditRevision, \
                           StoryCharacterRevision, StoryGroupRevision, \
                           PublisherCodeNumberRevision
from apps.oi.views import DISPLAY_CLASSES, REVISION_CLASSES, CTYPES

MODEL_NAMES = [
    'publisher', 'brand', 'indicia_publisher', 'series', 'brand_group',
    'brand_use',
    # 'series_bond',
    # 'creator',  # CreatorNameDetails, birth/death dates
    'creator_art_influence', 'received_award', 'creator_degree',
    'creator_membership',
    # 'creator_non_comic_work',
    'creator_relation', 'creator_school', 'award', 'feature',
    'feature_logo', 'feature_relation', 'printer', 'indicia_printer',
    # 'character',  # CharacterNameDetails
    'group', 'group_membership', 'character_relation', 'group_relation',
    'universe', 'story_arc', 'story_arc_relation',
]


class Command(BaseCommand):
    help = ('Create approved changesets for existing display objects, so '
            'that data imported from a comics.org dump can be edited.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int, default=500,
            help='Number of objects per class to process (default 500, '
                 '0 for all).')

    def handle(self, *args, **options):
        self.limit = options['limit'] or None
        self.anon = User.objects.get(username='anon')

        for model_name in MODEL_NAMES:
            self.setup_object_class(model_name)
        self.setup_issues()

    def _slice(self, queryset):
        return queryset[:self.limit] if self.limit else queryset

    def setup_object(self, display_object, model_name):
        changeset = Changeset(indexer=self.anon,
                              approver=self.anon,
                              state=states.APPROVED,
                              change_type=CTYPES[model_name])
        changeset.created = display_object.modified
        changeset.save()
        changeset.comments.create(
            commenter=self.anon,
            text='This is an automatically generated change '
                 'for development purposes.',
            old_state=states.APPROVED,
            new_state=states.APPROVED)
        comment = changeset.comments.all()[0]
        comment.created = display_object.modified
        comment.save()
        revision = REVISION_CLASSES[model_name].clone(
            display_object, changeset, fork=True)
        revision.source = display_object
        revision.created = display_object.modified
        revision.save()
        return changeset

    def setup_object_class(self, model_name):
        objects = DISPLAY_CLASSES[model_name].objects.order_by('id')
        self.stdout.write('Setting up: %s' % model_name)
        for display_object in self._slice(objects):
            self.setup_object(display_object, model_name)

    def setup_issue(self, issue):
        changeset = self.setup_object(issue, 'issue')
        issue_revision = changeset.issuerevisions.get()
        for credit in issue.active_credits:
            revision = IssueCreditRevision.clone(
                credit, changeset, issue_revision=issue_revision, fork=True)
            revision.source = credit
            revision.created = credit.modified
            revision.save()
        for story in issue.active_stories():
            story_revision = StoryRevision.clone(story, changeset, fork=True)
            story_revision.source = story
            story_revision.created = story.modified
            story_revision.save()
            for credit in story.active_credits:
                revision = StoryCreditRevision.clone(
                    credit, changeset, story_revision=story_revision,
                    fork=True)
                revision.source = credit
                revision.created = credit.modified
                revision.save()
            for character in story.active_characters:
                revision = StoryCharacterRevision.clone(
                    character, changeset, story_revision=story_revision,
                    fork=True)
                revision.source = character
                revision.created = character.modified
                revision.save()
            for group in story.active_groups:
                revision = StoryGroupRevision.clone(
                    group, changeset, story_revision=story_revision,
                    fork=True)
                revision.source = group
                revision.created = group.modified
                revision.save()
        for code_number in issue.active_code_numbers():
            revision = PublisherCodeNumberRevision.clone(
                code_number, changeset, fork=True,
                issue_revision=issue_revision)
            revision.source = code_number
            revision.created = code_number.modified
            revision.save()

    def setup_issues(self):
        self.stdout.write('Setting up: Issues')
        for issue in self._slice(Issue.objects.order_by('id')):
            self.setup_issue(issue)
