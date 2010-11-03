from django.core.cache import cache
from sorl.thumbnail.backends.base import ThumbnailBackendBase
from sorl.thumbnail.models import KeyStore
from sorl.thumbnail.conf import settings


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

    def _store_empty_all(self):
        for ks in KeyStore.objects.all():
            cache.delete(ks.key)
        KeyStore.objects.all().delete()

