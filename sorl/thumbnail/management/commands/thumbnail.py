from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_duration

from sorl.thumbnail import default
from sorl.thumbnail.images import delete_all_thumbnails


VALID_LABELS = ['cleanup', 'clear', 'clear_delete_referenced', 'clear_delete_all']


class Command(BaseCommand):
    help = "Handles thumbnails and key-value store"
    missing_args_message = "Enter a valid operation: {}".format(
        ", ".join(VALID_LABELS)
    )

    def add_arguments(self, parser):
        parser.add_argument('args', choices=VALID_LABELS, nargs=1)
        parser.add_argument('--timeout')

    # flake8: noqa: C901
    def handle(self, *labels, **options):
        verbosity = int(options.get('verbosity'))
        label = labels[0]

        if label == 'cleanup':
            if verbosity >= 1:
                self.stdout.write("Cleanup thumbnails", ending=' ... ')

            default.kvstore.cleanup()

            if verbosity >= 1:
                self.stdout.write("[Done]")

            return

        if label == 'clear_delete_referenced':
            timeout_date = None
            if options['timeout']:
                # Optional deletion timeout duration
                if options['timeout'].isdigit():  # A number of seconds
                    seconds = int(options['timeout'])
                else:
                    # A duration string as supported by Django.
                    duration = parse_duration(options['timeout'])
                    if not duration:
                        raise CommandError(f"Unable to parse '{options['timeout']}' as a duration")
                    seconds = duration.seconds
                timeout_date = timezone.now() - timedelta(seconds=seconds)
            if verbosity >= 1:
                msg = "Delete all thumbnail files referenced in Key Value Store"
                if timeout_date:
                    msg += f" older than {timeout_date.strftime('%Y-%m-%d %H:%M:%S')}"
                self.stdout.write(msg, ending=' ... ')

            default.kvstore.delete_all_thumbnail_files(older_than=timeout_date)

            if verbosity >= 1:
                self.stdout.write('[Done]')

        if verbosity >= 1:
            self.stdout.write("Clear the Key Value Store", ending=' ... ')

        default.kvstore.clear()

        if verbosity >= 1:
            self.stdout.write('[Done]')

        if label == 'clear_delete_all':
            if verbosity >= 1:
                self.stdout.write("Delete all thumbnail files in THUMBNAIL_PREFIX", ending=' ... ')

            delete_all_thumbnails()

            if verbosity >= 1:
                self.stdout.write('[Done]')

    def create_parser(self, prog_name, subcommand, **kwargs):
        kwargs['epilog'] = (
            "Documentation: https://sorl-thumbnail.readthedocs.io/en/latest/management.html"
        )
        return super().create_parser(prog_name, subcommand, **kwargs)
