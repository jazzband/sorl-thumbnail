from __future__ import with_statement
import re
import os
from django.utils.encoding import smart_str, DEFAULT_LOCALE_ENCODING
from sorl.thumbnail.base import EXTENSIONS
from sorl.thumbnail.engines.base import EngineBase
from subprocess import Popen, PIPE
from tempfile import mkstemp
from django.utils.datastructures import SortedDict
from sorl.thumbnail.conf import settings


size_re = re.compile(r'^(?:.+) (?:[A-Z]+) (?P<x>\d+)x(?P<y>\d+)')


class Engine(EngineBase):
    """
    Image object is a tuple of a pathname and a dict with options convert
    """
    def write(self, image, options, thumbnail):
        """
        Writes the thumbnail image
        """
        out = mkstemp(suffix='.%s' % EXTENSIONS[options['format']])[1]
        args = [settings.THUMBNAIL_CONVERT, image['source']]
        for k, v in image['options'].iteritems():
            args.append('-%s' % k)
            args.append('%s' % v)
        args.append(out)
        args = map(smart_str, args)
        p = Popen(args)
        p.wait()
        with open(out, 'r') as fp:
            thumbnail.write(fp.read())
        os.remove(out)
        os.remove(image['source']) # we should not need this now

    def get_image(self, source):
        """
        Returns the backend image objects from a ImageFile instance
        """
        tmp = mkstemp()[1]
        with open(tmp, 'w') as fp:
            fp.write(source.read())
        return {'source': tmp, 'options': SortedDict(), 'size': None}

    def get_image_size(self, image):
        """
        Returns the image width and height as a tuple
        """
        if image['size'] is None:
            p = Popen([settings.THUMBNAIL_IDENTIFY, image['source']], stdout=PIPE)
            p.wait()
            m = size_re.match(p.stdout.read())
            image['size'] = int(m.group('x')), int(m.group('y'))
        return image['size']

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

    def _crop(self, image, width, height, x_offset, y_offset):
        """
        Crops the image
        """
        image['options']['crop'] = '%sx%s+%s+%s' % (
            width, height, x_offset, y_offset
            )
        image['size'] = (width, height) # update image size
        return image

    def _scale(self, image, width, height):
        """
        Does the resizing of the image
        """
        image['options']['scale'] = '%sx%s!' % (width, height)
        image['size'] = (width, height) # update image size
        return image

    def _get_raw_data(self, image, format_, quality):
        """
        Gets raw data given the image, format and quality
        """
        raise NotImplemented()

