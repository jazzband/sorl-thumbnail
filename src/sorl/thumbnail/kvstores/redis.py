from ..redis import Redis
from sorl.thumbnail.kvstores.base import KVStoreBase, add_prefix
from sorl.thumbnail.conf import settings
from sorl.thumbnail.storage import deserialize_image_file


class KVStore(KVStoreBase):
    def __init__(self, *args, **kwargs):
        super(KVStore, self).__init__(*args, **kwargs)
        self.connection = Redis(
            host=settings.THUMBNAIL_REDIS_HOST,
            port=settings.THUMBNAIL_REDIS_PORT,
            db=settings.THUMBNAIL_REDIS_DB,
            )

    def _get_raw(self, key):
        return self.connection.get(key)

    def _set_raw(self, key, value):
        return self.connection.set(key, value)

    def _delete_raw(self, key):
        return self.connection.delete(key)

    def _find_keys(self, identity):
        pattern = add_prefix('*', identity)
        return self.connection.keys(pattern=pattern)

