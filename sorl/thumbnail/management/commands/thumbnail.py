from django.core.management.base import BaseCommand, CommandError
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class


class Command(BaseCommand):
    help = (
        u'Handles thumbnails and key value store'
    )
    args = '[cleanup, clear]'
    option_list = BaseCommand.option_list

    def handle(self, cmd, *args, **kwargs):
        if cmd not in ['cleanup', 'clear']:
            raise CommandError('`%s` is not a valid argument' % cmd)
        kvstore = get_module_class(settings.THUMBNAIL_KVSTORE)()
        if cmd == 'cleanup':
            kvstore.cleanup()
            print 'Cleanup thumbnails done.'
        if cmd == 'clear':
            kvstore.clear()
            print 'Cleared the Key Value Store.'

