from django.utils.functional import LazyObject, SimpleLazyObject

from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class
from sorl.thumbnail.kvstores.cached_db_kvstore import KVStore

class Backend(LazyObject):
    def _setup(self):
        self._wrapped = get_module_class(settings.THUMBNAIL_BACKEND)()


class Engine(LazyObject):
    def _setup(self):
        self._wrapped = get_module_class(settings.THUMBNAIL_ENGINE)()


class Storage(LazyObject):
    def _setup(self):
        self._wrapped = get_module_class(settings.THUMBNAIL_STORAGE)()


backend = Backend()
kvstore = SimpleLazyObject(lambda: KVStore())
engine = Engine()
storage = Storage()
