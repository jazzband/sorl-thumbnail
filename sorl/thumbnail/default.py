from django.utils.functional import LazyObject

from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class


STORAGE_INIT_PARAMS = {
    'S3BotoStorage': {
        'bucket_name': 'THUMBNAIL_STORAGE_AWS_BUCKET_NAME'
    }
}


class Backend(LazyObject):
    def _setup(self):
        self._wrapped = get_module_class(settings.THUMBNAIL_BACKEND)()


class KVStore(LazyObject):
    def _setup(self):
        self._wrapped = get_module_class(settings.THUMBNAIL_KVSTORE)()


class Engine(LazyObject):
    def _setup(self):
        self._wrapped = get_module_class(settings.THUMBNAIL_ENGINE)()


class Storage(LazyObject):
    def _setup(self):
        klass = get_module_class(settings.THUMBNAIL_STORAGE)
        kwargs = {}
        for param, settings_param in STORAGE_INIT_PARAMS.get(klass.__name__, {}).items():
            if hasattr(settings, settings_param):
                kwargs[param] = getattr(settings, settings_param)
        self._wrapped = klass(**kwargs)


backend = Backend()
kvstore = KVStore()
engine = Engine()
storage = Storage()
