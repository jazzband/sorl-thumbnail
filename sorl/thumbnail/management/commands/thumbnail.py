from django.core.management.base import BaseCommand, CommandError
from sorl.thumbnail.conf import settings
from sorl.thumbnail import default


class Command(BaseCommand):
    help = (
        u'Handles thumbnails and key value store'
    )
    args = '[cleanup, clear]'
    option_list = BaseCommand.option_list

    def handle(self, *labels, **options):
        verbosity = int(options.get('verbosity'))
        if len(labels) != 1:
            raise CommandError('`%s` is not a valid argument' % labels)

        label = labels[0]

        if label not in ['cleanup', 'clear']:
            raise CommandError('`%s` unknown action' % label)

        if label == 'cleanup':
            if verbosity >= 1:
                self.stdout.write("Cleanup thumbnails ... ")

            default.kvstore.cleanup()

            if verbosity >= 1:
                self.stdout.write("[Done]\n")

        if label == 'clear':
            if verbosity >= 1:
                self.stdout.write("Clear the Key Value Store ... ")

            default.kvstore.clear()

            if verbosity >= 1:
                self.stdout.write("[Done]\n")

