import re
import os
from __future__ import with_statement
from sorl.thumbnail.engines.base import EngineBase
from tempfile import mkstemp
from subprocess import Popen, PIPE
from django.utils.encoding import smart_str, DEFAULT_LOCALE_ENCODING


size_re = re.compile(r'^(?:.+) (?:[A_Z]+) (?P<x>\d+)x(?P<y>\d+)')


class Engine(EngineBase):
    """
    Image object is a tuple of a pathname and a dict with options convert
    """
    def get_image(self, source):
        """
        Returns the backend image objects from a ImageFile instance
        """
        image = mkstemp()[1]
        with open(image, 'w') as fp:
            image.write(source.read())
        return {'file': image, 'options': {}, 'size': None}

    def get_image_size(self, image):
        """
        Returns the image width and height as a tuple
        """
        if image['size'] is None:
            p = Popen([settings.THUMBNAIL_IDENTIFY, image['file']], stdout=PIPE)
            p.wait()
            m = size_re.match(p.stdout.read())
            image['size'] = m.group('x'), group('y')
        return image['size']

    def dummy_image(self, width, height):
        """
        Returns a generated dummy image object with size given. The dummy image
        from the shipped engines are grey (240) and has a darker cross (128)
        over them.
        """
        raise NotImplemented()

    def is_valid_image(self, raw_data):
        """
        Checks if the supplied raw data is valid image data
        """
        tmp = mkstemp()[1]
        with open(tmp, 'w') as fp:
            tmp.write(raw_data)
            p = Popen([settings.THUMBNAIL_IDENTIFY, tmp])
            retcode = p.wait()
        os.remove(tmp)
        return retcode == 0

    def _colorspace(self, image, colorspace):
        """
        `Valid colorspaces
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-colorspace>`_.
        Backends need to implement the following::

            RGB, GRAY
        """
        image['options']['colorspace'] = colorspace
        return image

    def _scale(self, image, width, height):
        """
        Does the resizing of the image
        """
        image['options']['scale'] = '%sx%s' % (width, height)
        return image

    def _crop(self, image, width, height, x_offset, y_offset):
        """
        Crops the image
        """
        raise NotImplemented()

    def _get_raw_data(self, image, format_, quality):
        """
        Gets raw data given the image, format and quality
        """
        raise NotImplemented()

