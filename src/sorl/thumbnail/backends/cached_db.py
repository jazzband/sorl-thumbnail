from django.core.cache import cache
from sorl.thumbnail.backends.base import ThumbnailBackendBase, add_prefix
from sorl.thumbnail.conf import settings
from sorl.thumbnail.models import KeyStore
from sorl.thumbnail.storage import deserialize_image_file


class EMPTY_VALUE(object):
    pass


class ThumbnailBackend(ThumbnailBackendBase):
    def _store_get_raw(self, key):
        value = cache.get(key)
        if value is None:
            try:
                value = KeyStore.objects.get(key=key).value
            except KeyStore.DoesNotExist:
                # we set the cache to prevent further db lookups
                value = EMPTY_VALUE
            cache.set(key, value, settings.THUMBNAIL_CACHE_TIMEOUT)
        if value == EMPTY_VALUE:
            return None
        return value

    def _store_set_raw(self, key, value):
        key_store = KeyStore.objects.get_or_create(key=key)[0]
        key_store.value = value
        key_store.save()
        cache.set(key, value, settings.THUMBNAIL_CACHE_TIMEOUT)

    def _store_delete_raw(self, key):
        KeyStore.objects.filter(key=key).delete()
        cache.delete(key)

    def _store_delete_orphans(self):
        start = add_prefix('', identity='image')
        qs = KeyStore.objects.filter(key__startswith=start)
        for ks in qs:
            image_file = deserialize_image_file(ks.value)
            if not image_file.exists():
                self.store_delete(image_file)

