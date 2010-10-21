from abs import ABCMeta, abstractmethod, abstractproperty
from django.utils.encoding import force_unicode


class ThumbnailBackendBase(object):
    __metaclass__ = ABCMeta

    extensions = {
        'JPEG': 'jpg',
        'PNG': 'png',
    }

    def __init__(self, fobj):
        self.fobj = fobj

    @abstractproperty
    def width(self):
        """
        Should return the width of the image after `process`
        """
        pass

    @abstractproperty
    def height(self):
        """
        Should return the height of the image after `process`
        """
        pass

    @abstractmethod
    def resize(self, geometry, crop=None):
        """
        `geometry` should be a sorl.thumbnail.helpers.Geometry instance

        `crop` is used in conjunction with the '^' modifier and will crop the
        resulting image to the specified width and height. The value of `crop`
        sets the gravity and should be specified as `GraphicsMagick gravity
        options
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-gravity>`_
        Backends need to implement the following::

            NorthWest, North, NorthEast, West, Center, East, SouthWest, South,
            SouthEast.

        """
        pass

    @abstractmethod
    def colorspace(self, value):
        """
        `Valid colorspaces
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-colorspace>`_.
        Backends need to implement the following::

            RGB, GRAY
        """
        pass

    @abstractmethod
    def sharpen(self, value):
        """
        Sharpens the image, `value` should be between 1 and 100
        """
        pass

    @abstractmethod
    def write(self, fobj, format=None, quality=None):
        """
        Writes the processed image data to File object
        """
        raise NotImplemented

    def process(self, geometry, crop=None, colorspace=None, sharpen=None,
                **kwargs):
        """
        Does the processing of the image
        """
        self.colorspace(colorspace)
        self.resize(geometry, crop)
        self.sharpen(sharpen)

    def get_filename(self, options, format):
        """
        Computes the destination filename.
        """
        base = get_unique_key(self.fobj.name, self.fobj.storage_string, options)
        ext = self.extensions[format]
        return '%s.%s' % (base, ext)


