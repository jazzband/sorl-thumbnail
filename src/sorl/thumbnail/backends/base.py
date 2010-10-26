from abc import ABCMeta, abstractmethod, abstractproperty
from sorl.thumbnail.storage import StorageImage
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class


class ThumbnailBase(object):
    __metaclass__ = ABCMeta

    _default_options = {
        'format': settings.THUMBNAIL_FORMAT,
        'quality': settings.THUMBNAIL_QUALITY,
        'colorspace': settings.THUMBNAIL_COLORSPACE,
        'upscale': settings.THUMBNAIL_UPSCALE,
        'crop': False,
    }

    def __init__(self, source, geometry, options, engine=None):
        """
        ``source``
            Should represent a file, will introspected by the
            ``sorl.thumbnail.storage.StorageImage`` constructor
        ``geometry``
            Geometry string
        ``options``
            Dictionary with options
        ``engine``
            ``sorl.thumbnail.engine.EngineBase`` sub class instance
        """
        self._source = StorageImage(source)
        self._geometry = geometry
        self._options = options
        for key, value in self._default_options.iteritems():
            self._options.setdefault(key, value)
        if engine is None:
            engine_cls = get_module_class(settings.THUMBNAIL_ENGINE)
            self._engine = engine_cls()
        else:
            self._enigne = engine
        self._prepare()

    @abstractmethod
    def _prepare(self):
        pass

    name = abstractproperty()
    url = abstractproperty()
    path = abstractproperty()
    width = abstractproperty()
    height = abstractproperty()
    # x, y aliases
    x = property(lambda self: self.width)
    y = property(lambda self: self.height)
    is_portrait = lambda self: self.y > self.x
    size = abstractproperty()

    @property
    def margin(self):
        """
        Returns the calculated marigin from requested geometry and thumbnail
        """
        margin = [0, 0, 0, 0]
        if self._geometry.x is not None:
            ex = self._geometry.x - self.x
            margin[3] = ex / 2
            margin[1] = ex / 2
            if ex % 2:
                margin[1] += 1
        if self._geometry.y is not None:
            ey = self._geometry.y - self.y
            margin[0] = ey / 2
            margin[2] = ey / 2
            if ey % 2:
                margin[2] += 1
        return ' '.join([ '%spx' % n for n in margin ])

