from __future__ import with_statement
import re
import os
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str
from sorl.thumbnail.base import EXTENSIONS
from sorl.thumbnail.conf import settings
from sorl.thumbnail.engines.base import EngineBase
from subprocess import Popen, PIPE
from tempfile import mkstemp, NamedTemporaryFile


size_re = re.compile(r'^(?:.+) (?:[A-Z]+) (?P<x>\d+)x(?P<y>\d+)')


class Engine(EngineBase):
    """
    Image object is a dict with source path, options and size
    """
    def write(self, image, options, thumbnail):
        """
        Writes the thumbnail image
        """
        if (
                options['format'] == 'JPEG' and
                options.get('progressive', settings.THUMBNAIL_PROGRESSIVE)
            ):
            image['options']['interlace'] = 'line'
        image['options']['quality'] = options['quality']
        args = settings.THUMBNAIL_CONVERT.split(' ')
        args.append(image['source'])
        for k, v in image['options'].iteritems():
            args.append('-%s' % k)
            if v is not None:
                args.append('%s' % v)

        try:
            with NamedTemporaryFile(suffix='.%s' % EXTENSIONS[options['format']], mode='rb') as fp:
                args.append(fp.name)
                args = map(smart_str, args)
                p = Popen(args)
                p.wait()
                thumbnail.write(fp.read())
        finally:
            os.remove(image['source']) # we should not need this now

    def get_image(self, source):
        """
        Returns the backend image objects from a ImageFile instance
        """
        with NamedTemporaryFile(mode='wb', delete=False) as fp:
            fp.write(source.read())
        return {'source': fp.name, 'options': SortedDict(), 'size': None}

    def get_image_size(self, image):
        """
        Returns the image width and height as a tuple
        """
        if image['size'] is None:
            args = settings.THUMBNAIL_IDENTIFY.split(' ')
            args.append(image['source'])
            p = Popen(args, stdout=PIPE)
            p.wait()
            m = size_re.match(p.stdout.read())
            image['size'] = int(m.group('x')), int(m.group('y'))
        return image['size']

    def is_valid_image(self, raw_data):
        """
        This is not very good for imagemagick because it will say anything is
        valid that it can use as input.
        """
        with NamedTemporaryFile(mode='wb') as fp:
            fp.write(raw_data)
            fp.flush()
            args = settings.THUMBNAIL_IDENTIFY.split(' ')
            args.append(fp.name)
            p = Popen(args)
            retcode = p.wait()
        return retcode == 0

    def _orientation(self, image):
        return image
        # XXX need to get the dimensions right after a transpose.
        if settings.THUMBNAIL_CONVERT.endswith('gm convert'):
            args = settings.THUMBNAIL_IDENTIFY.split()
            args.extend([ '-format', '%[exif:orientation]', image['source'] ])
            p = Popen(args, stdout=PIPE)
            p.wait()
            result = p.stdout.read().strip()
            if result and result != 'unknown':
                result = int(result)
                options = image['options']
                if result == 2:
                    options['flop'] = None
                elif result == 3:
                    options['rotate'] = '180'
                elif result == 4:
                    options['flip'] = None
                elif result == 5:
                    options['rotate'] = '90'
                    options['flop'] = None
                elif result == 6:
                    options['rotate'] = '90'
                elif result == 7:
                    options['rotate'] = '-90'
                    options['flop'] = None
                elif result == 8:
                    options['rotate'] = '-90'
        else:
            # ImageMagick also corrects the orientation exif data for
            # destination
            image['options']['auto-orient'] = None
        return image

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

