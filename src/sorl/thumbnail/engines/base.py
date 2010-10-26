#coding=utf-8
import re
from abc import ABCMeta, abstractmethod
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class, mkhash, dict_serialize
from sorl.thumbnail.helpers import ThumbnailError
from sorl.thumbnail.storage import SuperImage


bgpos_pat = re.compile(r'^(?P<value>\d+)(?P<unit>%|px)$')
geometry_pat = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?$')


class ThumbnailEngineBase(object):
    """
    ABC from Thumbnail engines, methods are static
    """
    __metaclass__ = ABCMeta

    extensions = {
        'JPEG': 'jpg',
        'PNG': 'png',
    }

    @abstractmethod
    def resize(self, image, geometry, options):
        """
        Does the resizing of the image
        """
        raise NotImplemented()

    @abstractmethod
    def colorspace(self, image, geometry, options):
        """
        `Valid colorspaces
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-colorspace>`_.
        Backends need to implement the following::

            RGB, GRAY
        """
        raise NotImplemented()

    @abstractmethod
    def create(self, source, geometry, options, thumbnail):
        """
        Should create the thumbnail and return it as a
        ``sorl.thumbnail.storage.SuperImage`` instance
        """
        raise NotImplemented()

    @abstractmethod
    def write(self, image, options, thumbnail):
        """
        Writes the thumbnail to storage
        """
        raise NotImplemented()

    def get(self, source, geometry, options):
        """
        Should return a ``sorl.thumbnail.storage.SuperImage``
        instance
        """
        name = self.get_filename(source, geometry, options)
        storage_cls = get_module_class(settings.THUMBNAIL_STORAGE)
        thumbnail = SuperImage(name, storage_cls())
        if thumbnail.exists():
            # We could have an overwrite option passed in to
            # ThumbnailEngine.get and delete it if existed but I am
            # that could lead to race conditions. There fore we just
            # return it.
            return thumbnail
        return self.create(source, geometry, options, thumbnail)

    def get_filename(self, source, geometry, options):
        """
        Computes the destination filename.
        """
        key = mkhash(source.name, source.storage_path, geometry,
                     dict_serialize(options))
        # make some subdirs
        path = '%s/%s/%s' % (key[:2], key[2:4], key)
        return '%s%s.%s' % (settings.THUMBNAIL_PREFIX, path,
                            self.extensions[options['format']])

    #
    # Helper methods for resize
    #
    def parse_crop(self, crop, image, box):
        """
        ``crop``
            Crop option string
        ``image``
            The thumbnail width and hight tuple
        ``box``
            The requested width and height tuple

        The box should be smaller than the image but it works out anyway
        """
        def syntax_error():
            raise ThumbnailError('Unrecognized crop option: %s' % crop)
        alias_to_percent = {
            'left': '0%',
            'center': '50%',
            'right': '100%',
            'top': '0%',
            'bottom': '100%',
        }
        crop_xy = crop.split(' ')
        if len(crop_xy) == 1:
            crop_xy *= 2
        if len(crop_xy) != 2:
            syntax_error()

        def get_offset(crop, epsilon):
            crop = alias_to_percent.get(crop, crop)
            m = bgpos_pat.match(crop)
            if not m:
                raise syntax_error()
            value = int(m.group('value')) # we only take ints in the regexp
            unit = m.group('unit')
            if unit == '%':
                value = epsilon * value / 100.0
            # return ∈ [0, epsilon]
            return int(max(0, min(value, epsilon)))

        offset_x = get_offset(crop_xy[0], image[0] - box[0])
        offset_y = get_offset(crop_xy[1], image[1] - box[1])
        return offset_x, offset_y, image[0] - offset_x, image[1] - offset_y

    def parse_geometry(self, geometry):
        """
        Parses a geometry string syntax and returns a (width, height) tuple
        """
        m = geometry_pat.match(geometry)
        def syntax_error():
            return ThumbnailError('Geometry does not have the correct '
                    'syntax: %s' % geometry)
        if not m:
            raise syntax_error()
        x = m.group('x')
        y = m.group('y')
        if x is None and y is None:
            raise syntax_error()
        if x is not None:
            x = int(x)
        if y is not None:
            y = int(y)
        return x, y


