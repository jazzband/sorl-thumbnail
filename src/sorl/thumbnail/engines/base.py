from abc import ABCMeta, abstractmethod
from sorl.thumbnail.helpers import mkhash, dict_serialize


class ThumbnailEngineBase(object):
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
        pass

    @abstractmethod
    def colorspace(self, image, geometry, options):
        """
        `Valid colorspaces
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-colorspace>`_.
        Backends need to implement the following::

            RGB, GRAY
        """
        pass

    @abstractmethod
    def create(self, source, geometry, options):
        """
        Should create the thumbnail and return it as a
        ``sorl.thumbnail.storage.StorageImage`` instance
        """
        pass

    @abstractmethod
    def write(self, image, name, options):
        """
        Writes the thumbnail to storage
        """
        pass

    def get_filename(self, source, geometry, options):
        """
        Computes the destination filename.
        """
        base = mkhash(source.name, source.storage_path, geometry,
                      dict_serialize(options))
        # make some subdirs
        base = '%s/%s/%s' % (base[:2], base[2:4], base)
        return '%s.%s' % (base, self.extensions[options['format']])

