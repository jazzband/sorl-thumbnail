import os

from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.utils.safestring import mark_safe
from django.utils.html import urlquote, conditional_escape

from base import Thumbnail, OPTIONS
from utils import thumbnail_basename

class DjangoThumbnail(Thumbnail):
    # filename_format is passed the following string options:
    #   `filename`   -- original source filename
    #   `basename`   -- source filename, minus its extensions if it was '.jpg'
    #   `directory`  -- source directory (relative to self.root)
    #   `thumbs_dir` -- optional thumbnail directory option (starting with a /
    #   `quality`    -- the quality of the image
    #   `options`    -- a list of any non-default settings, each starting with
    #                   an underscore
    #   `x` and `y`  -- thumbnail size (not guaranteed to match actual image
    #                   dimensions)
    filename_format = '%(thumbs_dir)s%(directory)s/%(basename)s_%(x)sx%(y)s%(options)s_q%(quality)s.jpg'
    root = settings.MEDIA_ROOT
    base_url = settings.MEDIA_URL

    def __init__(self, relative_source_path, thumbs_dir='thumbs', *args,
                 **kwargs):
        self.thumbs_dir = thumbs_dir
        self.relative_source_path = relative_source_path
        source_path = self._absolute_path(relative_source_path)
        super(DjangoThumbnail, self).__init__(source_path, '',
                                              generate_thumbnail=False,
                                              *args, **kwargs)
        # Bit of a work-around here. The dynamic thumbnail name needs to be
        # generated after the super __init__ so that the options are available.
        self.thumbnail_path = self._absolute_path(self.relative_thumbnail_path)
        self.generate_thumbnail()

    def _absolute_path(self, path):
        return os.path.join(self.root, path).encode(settings.FILE_CHARSET)

    def _get_relative_thumbnail_path(self):
        if hasattr(self, '_relative_thumbnail_path'):
            return self._relative_thumbnail_path
        source_dir, source_filename = os.path.split(self.relative_source_path)
        basename = thumbnail_basename(source_filename)

        options = ['_%s' % option for option in OPTIONS if getattr(self, option)]
        thumbs_dir = self.thumbs_dir or ''
        if thumbs_dir and not thumbs_dir.endswith('/'):
            thumbs_dir = '%s/' % thumbs_dir
        filename_opts = dict(
            thumbs_dir=thumbs_dir,
            filename=source_filename,
            basename=basename,
            directory=source_dir,
            x=self.size[0],
            y=self.size[1],
            quality=self.quality,
            options=''.join(options)
        )
        self._relative_thumbnail_path = self.filename_format % filename_opts
        return self._relative_thumbnail_path
    relative_thumbnail_path = property(_get_relative_thumbnail_path)

    def _get_url(self):
        bits = self.relative_thumbnail_path.split(os.path.sep)
        return iri_to_uri('%s%s' % (self.base_url, '/'.join(bits)))
    url = property(_get_url)

    def __unicode__(self):
        return self.url

    def img_tag(self, extra_attributes=None, dimensions=True):
        """
        Build the <img> HTML tag.
        
        Pass a dictionary to `extra_attributes` to provide other HTML attributes
        for the tag.

        If `dimensions` is true, then width and height attributes will be
        calculated from the thumbnail image size.
        """ 
        attributes = {'alt':''}
        if dimensions:
            size = self.thumbnail.size
            attributes['width'] = size[0]
            attributes['height'] = size[1]
        if extra_attributes:
            attributes.update(extra_attributes)
        attributes['src'] = self.url
        html_attributes = [' %s="%s"' % (k, conditional_escape(v))\
                           for k, v in attributes.items()]
        return mark_safe('<img%s />' % ''.join(html_attributes))
