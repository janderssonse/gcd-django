"""
Create a small, realistic set of interlinked records so a development
database is populated and clickable without a production dump (which
requires a comics.org login).

The graph reaches all the way down the hot paths — publishers → series →
issues → stories → credits → creators, plus a cover per issue — so the
public detail pages (issue, creator) actually render content and the
perf/count work has something real to run against.

Idempotent: uses fixed primary keys in a reserved high range and
get_or_create, so running it repeatedly is safe.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.stddata.models import Country, Language, Script, Date
from apps.gcd.models import (Publisher, Series, Issue, Story, StoryType,
                             CreditType, StoryCredit, Cover, Creator,
                             CreatorNameDetail)

# Reserved high id range, unlikely to collide with a real dump. Derived
# ids stay well under the 32-bit AutoField ceiling (~2.1e9).
BASE = 990000
STORY_ID_OFFSET = 900000000    # story id  = issue.id + offset
COVER_ID_OFFSET = 800000000    # cover id  = issue.id + offset

PUBLISHERS = [
    (BASE + 1, 'Sample Comics', 1938),
    (BASE + 2, 'Second Sample Press', 1965),
]

# (id, publisher_index, name, year, issue_numbers)
SERIES = [
    (BASE + 1, 0, 'The Sample Adventures', 1938, ['1', '2', '3']),
    (BASE + 2, 0, 'Sample Tales', 1952, ['1', '2']),
    (BASE + 3, 1, 'Modern Samples', 1965, ['1']),
]

# (id, official name). One creator per common role.
CREATORS = [
    (BASE + 1, 'Ada Sampleton'),
    (BASE + 2, 'Ben Exampleman'),
    (BASE + 3, 'Cora Placeholder'),
]

# The canonical credit types (id/name/sort_code) as the codebase uses
# them; not seeded by migrations, so create them. Maps to CREDIT_TYPES in
# apps/gcd/models/story.py. Value = (name, creator_index for the credit).
CREDITS = [
    (1, 'script', 0),
    (2, 'pencils', 1),
    (3, 'inks', 2),
    (4, 'colors', 1),
    (5, 'letters', 0),
    (6, 'editing', 2),
]


class Command(BaseCommand):
    help = ('Populate the database with a small sample of interlinked '
            'publishers, series, issues, stories, credits, creators and '
            'covers for development.')

    @transaction.atomic
    def handle(self, *args, **options):
        country, _ = Country.objects.get_or_create(
            id=BASE, defaults={'code': 'xd', 'name': 'Sampleland'})
        language, _ = Language.objects.get_or_create(
            id=BASE, defaults={'code': 'xd', 'name': 'Samplish'})
        # CreatorNameDetail.in_script defaults to this row; ensure it exists.
        script, _ = Script.objects.get_or_create(
            id=Script.LATIN_PK,
            defaults={'code': 'Latn', 'number': Script.LATIN_PK,
                      'name': 'Latin'})

        credit_types = {}
        for pk, name, _creator_idx in CREDITS:
            credit_types[name], _ = CreditType.objects.get_or_create(
                id=pk, defaults={'name': name, 'sort_code': pk})

        creators = []
        for pk, name in CREATORS:
            # birth/death must be Date rows (blank is fine): __str__ and the
            # creator page's display_birthday/display_deathday dereference
            # date.year, so null FKs would crash any page listing the
            # creator. Real data always has these (the OI add flow creates
            # them), so set both to stay valid by construction.
            birth, _ = Date.objects.get_or_create(id=pk)
            death, _ = Date.objects.get_or_create(id=pk + 10)
            creator, _ = Creator.objects.get_or_create(
                id=pk, defaults={'gcd_official_name': name,
                                 'sort_name': name, 'birth_date': birth,
                                 'death_date': death})
            # Exactly one official name detail is required for the creator
            # page and credit display to resolve.
            CreatorNameDetail.objects.get_or_create(
                id=pk, defaults={'name': name, 'sort_name': name,
                                 'creator': creator, 'in_script': script,
                                 'is_official_name': True})
            creators.append(creator)

        official_names = [c.creator_names.get(is_official_name=True)
                          for c in creators]
        comic_story = StoryType.objects.get(name='comic story')

        publishers = []
        for pk, name, year in PUBLISHERS:
            pub, _ = Publisher.objects.get_or_create(
                id=pk, defaults={'name': name, 'country': country,
                                 'year_began': year})
            publishers.append(pub)

        issue_total = story_total = 0
        for pk, pub_idx, name, year, numbers in SERIES:
            publisher = publishers[pub_idx]
            series, _ = Series.objects.get_or_create(
                id=pk, defaults={
                    'name': name, 'sort_name': name, 'year_began': year,
                    'country': country, 'language': language,
                    'publisher': publisher, 'is_comics_publication': True,
                    'has_gallery': False,
                    'publication_dates': '%d - present' % year})

            first = last = None
            for sort_code, number in enumerate(numbers):
                issue, _ = Issue.objects.get_or_create(
                    id=pk * 100 + sort_code, defaults={
                        'number': number, 'series': series,
                        'sort_code': sort_code,
                        'publication_date': '%d' % (year + sort_code),
                        'key_date': '%d-01-00' % (year + sort_code)})
                self._add_story(issue, comic_story, name, number,
                                credit_types, official_names)
                Cover.objects.get_or_create(
                    id=COVER_ID_OFFSET + issue.id,
                    defaults={'issue': issue})
                story_total += 1
                first = first or issue
                last = issue
            series.first_issue = first
            series.last_issue = last
            series.issue_count = len(numbers)
            series.save()
            issue_total += len(numbers)

        for publisher in publishers:
            publisher.series_count = publisher.series_set.count()
            publisher.issue_count = sum(
                s.issue_count for s in publisher.series_set.all())
            publisher.save()

        self.stdout.write(self.style.SUCCESS(
            'Sample data ready: %d publishers, %d series, %d issues, '
            '%d stories, %d creators.'
            % (len(publishers), len(SERIES), issue_total, story_total,
               len(CREATORS))))

    def _add_story(self, issue, comic_story, series_name, number,
                   credit_types, official_names):
        """One comic story on the issue, credited both as plaintext (what
        the credits templatetag reads) and as linked StoryCredit rows."""
        credited = {name: official_names[idx].name
                    for _pk, name, idx in CREDITS}
        story, created = Story.objects.get_or_create(
            id=STORY_ID_OFFSET + issue.id,
            defaults={'issue': issue, 'type': comic_story,
                      'sequence_number': 0, 'page_count': 8,
                      'title': '%s #%s' % (series_name, number),
                      'feature': series_name, **credited})
        if not created:
            return
        for _pk, name, idx in CREDITS:
            StoryCredit.objects.create(
                story=story, creator=official_names[idx],
                credit_type=credit_types[name])
