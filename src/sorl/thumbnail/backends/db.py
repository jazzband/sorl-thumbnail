from sorl.thumbnail.backends.base import ThumbnailBase
from sorl.thumbnail import models
from sorl.thumbnail.helpers import dict_serialize, mkhash


class Thumbnail(ThumbnailBase):
    def _prepare(self):
        options = dict_serialize(self._options)
        key = mkhash(self._source.name, self._source.storage_path,
                     self._geometry, options)
        try:
            self._thumbnail = models.Thumbnail.cache.get(key)
        except models.Thumbnail.DoesNotExist:
            thumbnail = self._engine.get(self._source, self._geometry,
                                         self._options)
            self._thumbnail = models.Thumbnail.cache.create(
                key = key,
                source_name=self._source.name,
                source_storage=self._source.storage_path,
                geometry=self._geometry,
                options=options,
                name=thumbnail.name,
                url=thumbnail.url,
                path=thumbnail.path,
                width=thumbnail.width,
                height=thumbnail.height,
                size=thumbnail.size,
                )

    name = property(lambda self: self._thumbnail.name)
    url = property(lambda self: self._thumbnail.url)
    path = property(lambda self: self._thumbnail.path)
    width = property(lambda self: self._thumbnail.width)
    height = property(lambda self: self._thumbnail.height)
    size = property(lambda self: self._thumbnail.size)

