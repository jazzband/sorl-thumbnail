from django.core.cache import cache
from sorl.thumbnail.kvstores.base import KVStoreBase, add_prefix
from sorl.thumbnail.conf import settings
from sorl.thumbnail.models import KVStore as KVStoreModel
from sorl.thumbnail.storage import deserialize_image_file


class EMPTY_VALUE(object):
    pass


class KVStore(KVStoreBase):
    def _get_raw(self, key):
        value = cache.get(key)
        if value is None:
            try:
                value = KVStoreModel.objects.get(key=key).value
            except KVStoreModel.DoesNotExist:
                # we set the cache to prevent further db lookups
                value = EMPTY_VALUE
            cache.set(key, value, settings.THUMBNAIL_CACHE_TIMEOUT)
        if value == EMPTY_VALUE:
            return None
        return value

    def _set_raw(self, key, value):
        kv = KVStoreModel.objects.get_or_create(key=key)[0]
        kv.value = value
        kv.save()
        cache.set(key, value, settings.THUMBNAIL_CACHE_TIMEOUT)

    def _delete_raw(self, key):
        KVStoreModel.objects.filter(key=key).delete()
        cache.delete(key)

    def _delete_orphans(self):
        start = add_prefix('', identity='image')
        qs = KVStoreModel.objects.filter(key__startswith=start)
        for value in qs.values_list('value', flat=True):
            image_file = deserialize_image_file(value)
            if not image_file.exists():
                self.delete(image_file)

