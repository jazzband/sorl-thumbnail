from django.core.files.storage import storages
from django.utils.functional import LazyObject

from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class


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
        if "." in settings.THUMBNAIL_STORAGE:
            self._wrapped = get_module_class(settings.THUMBNAIL_STORAGE)()
        else:
            self._wrapped = storages[settings.THUMBNAIL_STORAGE]


backend = Backend()
kvstore = KVStore()
engine = Engine()
storage = Storage()
