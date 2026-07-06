import glob
from os.path import abspath, basename, dirname, join

from django.core.management import call_command
from django.core.management.base import BaseCommand

# The project root, four levels up from this file.
BASE_DIR = abspath(join(dirname(__file__), '..', '..', '..', '..'))

# Fixtures that should not be part of a default development setup.
EXCLUDED = ('beta-users',)


class Command(BaseCommand):
    help = ('Set up a development database: run migrate, then load all '
            'app fixtures. Safe to re-run.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-migrate', action='store_true',
            help='Skip the migrate step and only load fixtures.')

    def handle(self, *args, **options):
        if not options['no_migrate']:
            call_command('migrate', interactive=False)

        fixtures = sorted(
            f for f in glob.glob(join(BASE_DIR, 'apps', '*', 'fixtures', '*'))
            if not basename(f).startswith(EXCLUDED))
        if not fixtures:
            self.stderr.write('No fixture files found.')
            return

        # A single loaddata call defers foreign key checks until all
        # fixtures are loaded, so the order does not matter.
        call_command('loaddata', *fixtures)
        self.stdout.write(self.style.SUCCESS(
            'Loaded %d fixture files.' % len(fixtures)))
