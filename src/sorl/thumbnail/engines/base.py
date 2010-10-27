#coding=utf-8
from abc import ABCMeta, abstractmethod
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import dict_serialize, get_module_class, mkhash
from sorl.thumbnail.helpers import ThumbnailError, toint
from sorl.thumbnail.parsers import parse_geometry, parse_crop
from sorl.thumbnail.storage import SuperImage


class ThumbnailEngineBase(object):
    """
    ABC from Thumbnail engines, methods are static
    """
    __metaclass__ = ABCMeta

    extensions = {
        'JPEG': 'jpg',
        'PNG': 'png',
    }

    def get(self, source, geometry_string, options):
        """
        Entry point. Should return a ``sorl.thumbnail.storage.SuperImage``
        instance
        """
        name = self.get_filename(source, geometry_string, options)
        storage_cls = get_module_class(settings.THUMBNAIL_STORAGE)
        thumbnail = SuperImage(name, storage_cls())
        if thumbnail.exists():
            # We could have an overwrite option passed in to
            # ThumbnailEngine.get and delete it if existed but I am
            # that could lead to race conditions. There fore we just
            # return it.
            return thumbnail
        image = self._get_image(source)
        image_x, image_y = self._get_image_dimensions(image)
        geometry = parse_geometry(geometry_string, (image_x, image_y))
        image = self.create(image, geometry, options)
        self.write(image, options, thumbnail)
        return thumbnail

    def create(self, image, geometry, options):
        """
        Processing conductor, returns the thumbnail as a backend image object
        """
        image = self.colorspace(image, geometry, options)
        image = self.resize(image, geometry, options)
        image = self.crop(image, geometry, options)
        return image

    def colorspace(self, image, geometry, options):
        """
        Wrapper for ``_colorspace``
        """
        colorspace = options['colorspace']
        return self._colorspace(image, colorspace)

    def resize(self, image, geometry, options):
        """
        Wrapper for ``_resize``
        """
        crop = options['crop']
        upscale = options['upscale']
        image_x, image_y = map(float, self._get_image_dimensions(image))
        # calculate scaling factor
        factors = (geometry[0] / image_x, geometry[1] / image_y)
        factor = max(factors) if crop else min(factors)
        if factor < 1 or upscale:
            width = toint(image_x * factor)
            height = toint(image_y * factor)
            image = self._resize(image, width, height)
        return image

    def crop(self, image, geometry, options):
        """
        Wrapper for ``_crop``
        """
        crop = options['crop']
        if not crop or crop == 'noop':
            return image
        image_x, image_y = self._get_image_dimensions(image)
        offset_x, offset_y = parse_crop(crop, (image_x, image_y), geometry)
        return self._crop(image, geometry[0], geometry[1], offset_x, offset_y)

    def write(self, image, options, thumbnail):
        """
        Wrapper for ``_write``
        """
        format_ = options['format']
        quality = options['quality']
        self._write(image, format_, quality, thumbnail)

    def get_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        key = mkhash(source.name, source.storage_path, geometry_string,
                     dict_serialize(options)) # we leave the engine path out
        # make some subdirs
        path = '%s/%s/%s' % (key[:2], key[2:4], key)
        return '%s%s.%s' % (settings.THUMBNAIL_PREFIX, path,
                            self.extensions[options['format']])

    #
    # Methods which backends need to implement
    # The ``image`` argument refers to a backend image object
    #
    @abstractmethod
    def _get_image(self, source):
        """
        Returns the backend image objects from a SuperImage instance
        """
        raise NotImplemented()

    @abstractmethod
    def _get_image_dimensions(self, image):
        """
        Returns the image width anf height as a tuple
        """
        raise NotImplemented()

    @abstractmethod
    def _colorspace(self, image, colorspace):
        """
        `Valid colorspaces
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-colorspace>`_.
        Backends need to implement the following::

            RGB, GRAY
        """
        raise NotImplemented()

    @abstractmethod
    def _resize(self, image, width, height):
        """
        Does the resizing of the image
        """
        raise NotImplemented()

    @abstractmethod
    def _crop(self, image, width, height, offset_x, offset_y):
        """
        Crops the image
        """
        raise NotImplemented()

    @abstractmethod
    def _write(self, image, format_, quality, thumbnail):
        """
        Writes to the thumbnail which is SuperImage instance
        """
        raise NotImplemented()


