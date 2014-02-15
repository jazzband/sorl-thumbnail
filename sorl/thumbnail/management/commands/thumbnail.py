# -*- encoding: utf8 -*-

from __future__ import unicode_literals, print_function

import sys

from django.core.management.base import BaseCommand, CommandError
from sorl.thumbnail import default


class Command(BaseCommand):
    help = (
        'Handles thumbnails and key value store'
    )
    args = '[cleanup, clear]'
    option_list = BaseCommand.option_list

    def handle(self, *labels, **options):
        verbosity = int(options.get('verbosity'))

        # Django 1.4 compatibility fix
        stdout = options.get('stdout', None)
        stdout = stdout if stdout else sys.stdout

        stderr = options.get('stderr', None)
        stderr = stderr if stderr else sys.stderr

        if not labels:
            print(self.print_help('thumbnail', ''), file=stderr)
            sys.exit(1)

        if len(labels) != 1:
            raise CommandError('`%s` is not a valid argument' % labels)

        label = labels[0]

        if label not in ['cleanup', 'clear']:
            raise CommandError('`%s` unknown action' % label)

        if label == 'cleanup':
            if verbosity >= 1:
                print("Cleanup thumbnails", end=' ... ', file=stdout)

            default.kvstore.cleanup()

            if verbosity >= 1:
                print("[Done]", file=stdout)

        elif label == 'clear':
            if verbosity >= 1:
                print("Clear the Key Value Store", end=' ... ', file=stdout)

            default.kvstore.clear()

            if verbosity >= 1:
                print('[Done]', file=stdout)
