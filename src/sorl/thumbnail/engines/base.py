#coding=utf-8
from abc import ABCMeta, abstractmethod
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import dict_serialize, get_module_class, tokey
from sorl.thumbnail.helpers import toint
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
        x_image, y_image = map(float, self.get_image_size(image))
        # calculate scaling factor
        factors = (geometry[0] / x_image, geometry[1] / y_image)
        factor = max(factors) if crop else min(factors)
        if factor < 1 or upscale:
            width = toint(x_image * factor)
            height = toint(y_image * factor)
            image = self._resize(image, width, height)
        return image

    def crop(self, image, geometry, options):
        """
        Wrapper for ``_crop``
        """
        crop = options['crop']
        if not crop or crop == 'noop':
            return image
        x_image, y_image = self.get_image_size(image)
        x_offset, y_offset = parse_crop(crop, (x_image, y_image), geometry)
        return self._crop(image, geometry[0], geometry[1], x_offset, y_offset)

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
        key = tokey(source.name, source.storage_path, geometry_string,
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
    def get_image(self, source):
        """
        Returns the backend image objects from a SuperImage instance
        """
        raise NotImplemented()

    @abstractmethod
    def get_image_size(self, image):
        """
        Returns the image width and height as a tuple
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
    def _crop(self, image, width, height, x_offset, y_offset):
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

