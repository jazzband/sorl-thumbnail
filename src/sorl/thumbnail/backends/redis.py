from ..redis import Redis
from sorl.thumbnail.conf import settings
from sorl.thumbnail.backends.base import ThumbnailBackendBase, prefix_key


class ThumbnailBackend(ThumbnailBackendBase):
    def __init__(self, *args, **kwargs):
        super(ThumbnailBackend, self).__init__(*args, **kwargs)
        self.connection = Redis(
            host=settings.THUMBNAIL_REDIS_HOST,
            port=settings.THUMBNAIL_REDIS_PORT,
            db=settings.THUMBNAIL_REDIS_DB,
            )

    def _store_get_raw(self, key):
        return self.connection.get(key)

    def _store_set_raw(self, key, value):
        return self.connection.set(key, value)

    def _store_delete_raw(self, key):
        return self.connection.delete(key)

    def _store_empty(self, prefix='image'):
        #TODO something doesnt work here
        pattern = prefix_key('*', prefix)
        keys = self.connection.keys(pattern=pattern)
        self.connection.delete(keys)

