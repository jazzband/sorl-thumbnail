from abc import ABCMeta, abstractmethod, abstractproperty
from sorl.thumbnail.helpers import mkhash


class ThumbnailEngineBase(object):
    __metaclass__ = ABCMeta

    extensions = {
        'JPEG': 'jpg',
        'PNG': 'png',
    }

    @abstractmethod
    def resize(self):
        """
        `geometry` should be a sorl.thumbnail.helpers.Geometry instance
        """
        pass

    @abstractmethod
    def colorspace(self):
        """
        `Valid colorspaces
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-colorspace>`_.
        Backends need to implement the following::

            RGB, GRAY
        """
        pass

    @abstractmethod
    def sharpen(self):
        """
        Sharpens the image, `value` should be between 1 and 100
        """
        pass

    @abstractmethod
    def write(self):
        """
        Writes the processed image data to File object
        """
        pass

    def process(self, landscape, portrait, crop=None, colorspace=None,
                sharpen=None, **kwargs):
        """
        Does the processing of the image
        """
        self.colorspace(colorspace)
        if self.width > self.height:
            geometry = landscape
        else:
            geometry = portrait
        self.resize(geometry, crop)
        self.sharpen(sharpen)

    def get_filename(self, options, format=None, **kwargs):
        """
        Computes the destination filename.
        """
        base = mkhash(self.fobj.name, self.fobj.storage_string, options)
        return '%s.%s' % (base, self.extensions[format])

