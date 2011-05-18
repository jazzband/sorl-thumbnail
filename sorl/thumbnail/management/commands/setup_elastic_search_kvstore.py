from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Make sure the needed index exists and put in a mapping so we it can query on _id."

    def handle_noargs(self, **options):
        from sorl.thumbnail.kvstores.elasticsearch_kvstore import setup_store
        setup_store()
