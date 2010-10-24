from abc import ABCMeta, abstractmethod, abstractproperty


class ThumbnailProxy(object):



class ThumbnailBase(ThumbnailProxy):
    __metaclass__ = ABCMeta

    def __init__(self, source, options, engine=None):
        """
        ``source``
            This should be a ``sorl.thumbnail.storage.StorageImage`` instance
        ``options``
            This should be a ``sorl.thumbnail.helpers.Options`` instance
        ``engine``
            This should be a ``sorl.thumbnail.engine.EngineBase`` sub class
            instance
        """
        self._source = source
        self._options = options
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
    x = property(lambda self: self.width)
    y = property(lambda self: self.height)
    is_portrait = lambda self: self.y > self.x
    size = abstractproperty()
    margin = abstractproperty()

