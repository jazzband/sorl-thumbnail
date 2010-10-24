from sorl.thumbnail.cache import ThumbnailBackendBase
from sorl.thumbnail import models
from sorl.thumbnail.helpers import get_storage_path


class Thumbnail(ThumbnailBase):
    def _prepare(self, source, options, engine=None):
        try:
            self._data = models.Thumbnail.datacache.get(
                source=self._source.name,
                source_storage=self._source.storage_path,
                options=unicode(self._options)
                )
        except models.Thumbnail.DoesNotExist:
            thumbnail = engine.process(self._source)
            self._thumbnail = Thumbnail.cache.create(
                source_name=self._source.name,
                source_storage=self._source.storage_path,
                source_width=self._source.width,
                source_height=self._source.height,
                options = unicode(self._options),
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
    margin = property(lambda self: self._thumbnail.css_margin())

