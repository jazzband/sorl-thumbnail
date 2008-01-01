import os
from django.conf import settings
from django.utils.encoding import iri_to_uri
from base import Thumbnail
from utils import get_thumbnail_setting


class DjangoThumbnail(Thumbnail):
    def __init__(self, relative_source, requested_size, opts=None,
                 quality=None, basedir=None, subdir=None, prefix=None):
        # Set the absolute filename for the source file
        source = self._absolute_path(relative_source)

        quality = get_thumbnail_setting('QUALITY', quality)
        imagemagick_path = get_thumbnail_setting('CONVERT')
        wvps_path = get_thumbnail_setting('WVPS')

        # Call super().__init__ now to set the opts attribute. generate() won't
        # get called because we are not setting the dest attribute yet.
        super(DjangoThumbnail, self).__init__(source, requested_size,
            opts=opts, quality=quality, imagemagick_path=imagemagick_path,
            wvps_path=wvps_path)
      
        # Get the relative filename for the thumbnail image, then set the
        # destination filename
        relative_thumbnail = \
           self._get_relative_thumbnail(relative_source, basedir=basedir,
                                        subdir=subdir, prefix=prefix)
        self.dest = self._absolute_path(relative_thumbnail)
        
        # Call generate now that the dest attribute has been set
        self.generate()

        # Set the relative & absolute url to the thumbnail
        self.relative_url = \
            iri_to_uri('/'.join(relative_thumbnail.split(os.sep)))
        self.absolute_url = '%s%s' % (settings.MEDIA_URL, self.relative_url)
    
    def _get_relative_thumbnail(self, relative_source, 
                                basedir=None, subdir=None, prefix=None):
        """
        Returns the thumbnail filename including relative path.
        """
        basedir = get_thumbnail_setting('BASEDIR', basedir)
        subdir = get_thumbnail_setting('SUBDIR', subdir)
        prefix = get_thumbnail_setting('PREFIX', prefix)
        path, filename = os.path.split(relative_source)
        basename, ext = os.path.splitext(filename)
        name = '%s%s' % (basename, ext.replace(".", "_"))
        size = '%sx%s' % self.requested_size
        opts_list = self.opts_list[:]
        opts_list.append('')
        opts = '_'.join(opts_list)
        thumbnail_filename = '%s%s_%s_%sq%s.jpg' % (prefix, name, size,
                                                    opts, self.quality)
        return os.path.join(basedir, path, subdir, thumbnail_filename)
    
    def _absolute_path(self, filename):
        absolute_filename = os.path.join(settings.MEDIA_ROOT, filename)
        return absolute_filename.encode(settings.FILE_CHARSET)

    def __unicode__(self):
        return self.absolute_url
