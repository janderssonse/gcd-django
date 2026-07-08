"""
Extract a small, connected subset from a loaded Tier-1 dump database into a
committed fixture the `just test-dump` lane runs on (see dumps/README.md).

Run against the loaded dump: `GCD_DB_NAME=test_dump manage.py sample_from_dump`
(the `just dump-extract` recipe does this). It reads whatever database the
connection points at and writes apps/gcd/tests/fixtures/dump_sample.json.

Strategy: seed with a few series that actually have stories/credits, pull in
their issues/stories/credits/creators/covers, then take the transitive
closure over foreign keys so the fixture is guaranteed loadable. Many-to-many
relations are dropped to bound the size (tests that need them build their own
data). Free-text notes are cleared so the committed fixture stays small.
"""

import json
import os

from django.apps import apps
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import DatabaseError

from apps.gcd.models import Series

FIXTURE = 'apps/gcd/tests/fixtures/dump_sample.json'
N_SERIES = 3
MAX_ISSUES_PER_SERIES = 8
MAX_STORIES_PER_ISSUE = 6
# Bulky free-text fields cleared so the fixture stays small and reviewable.
TEXT_FIELDS_TO_CLEAR = {'notes', 'tracking_notes', 'publication_notes',
                        'characters', 'synopsis', 'bio', 'reprint_notes'}


class Command(BaseCommand):
    help = ('Extract a connected subset from the loaded dump database into '
            'the committed dump_sample fixture.')

    def handle(self, *args, **options):
        self.seen = set()          # (label, pk)
        self.collected = []        # model instances, dependency-closed below

        series_qs = (Series.objects
                     .filter(issue__story__credits__isnull=False,
                             deleted=False)
                     .distinct().order_by('id')[:N_SERIES])
        if not series_qs:
            self.stderr.write('No series with credited stories found; is the '
                              'dump loaded into this database?')
            return

        for series in series_qs:
            self._add(series)
            issues = (series.issue_set.filter(deleted=False)
                      .order_by('sort_code')[:MAX_ISSUES_PER_SERIES])
            for issue in issues:
                self._add(issue)
                # (covers are not part of the public dump, so none here)
                stories = (issue.story_set.filter(deleted=False)
                           .order_by('sequence_number')[:MAX_STORIES_PER_ISSUE])
                for story in stories:
                    self._add(story)
                    for credit in story.credits.filter(deleted=False):
                        self._add(credit)

        self._close_over_foreign_keys()
        self._write_fixture()

    def _add(self, obj):
        if obj is None:
            return False
        key = (obj._meta.label, obj.pk)
        if key in self.seen:
            return False
        self.seen.add(key)
        self.collected.append(obj)
        return True

    def _close_over_foreign_keys(self):
        """Pull in every FK target of every collected object so the fixture
        has no dangling references. FK targets whose row is absent (the dump
        is data-only, so e.g. an auth user may be missing) are skipped and
        nulled out at serialization time."""
        queue = list(self.collected)
        while queue:
            obj = queue.pop()
            for field in obj._meta.get_fields():
                if not (field.concrete and field.is_relation
                        and (field.many_to_one or field.one_to_one)):
                    continue
                try:
                    target = getattr(obj, field.name)
                except (ObjectDoesNotExist, DatabaseError):
                    continue  # dangling FK, or FK into a table the dump omits
                if self._add(target):
                    queue.append(target)

    def _write_fixture(self):
        # Serialize per model, whitelisting only local (concrete) fields, so
        # the serializer never queries a many-to-many through table -- several
        # (e.g. external links, covers) are absent from the data-only dump.
        by_model = {}
        for obj in self.collected:
            by_model.setdefault(type(obj), []).append(obj)

        records = []
        for model, objs in by_model.items():
            local = model._meta.local_fields
            whitelist = {f.name for f in local} | {f.attname for f in local}
            records.extend(
                serializers.serialize('python', objs, fields=whitelist))

        present = self.seen
        for record in records:
            model = apps.get_model(record['model'])
            fk_by_name = {f.name: f for f in model._meta.get_fields()
                          if f.concrete and f.is_relation
                          and (f.many_to_one or f.one_to_one)}
            for name in list(record['fields']):
                if name in TEXT_FIELDS_TO_CLEAR:
                    record['fields'][name] = ''
                    continue
                fk = fk_by_name.get(name)
                value = record['fields'][name]
                if fk is not None and value is not None:
                    label = fk.related_model._meta.label
                    if (label, value) not in present:
                        record['fields'][name] = None  # target not collected

        text = json.dumps(records, indent=1, default=str)
        os.makedirs(os.path.dirname(FIXTURE), exist_ok=True)
        with open(FIXTURE, 'w') as handle:
            handle.write(text)

        counts = {}
        for label, _pk in self.seen:
            counts[label] = counts.get(label, 0) + 1
        self.stdout.write(self.style.SUCCESS(
            '%d objects -> %s' % (len(self.collected), FIXTURE)))
        for label in sorted(counts):
            self.stdout.write('  %-32s %d' % (label, counts[label]))
