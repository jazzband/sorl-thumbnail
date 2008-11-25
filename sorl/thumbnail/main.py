import os

from django.conf import settings
from django.utils.encoding import iri_to_uri, force_unicode

from sorl.thumbnail.base import Thumbnail
from sorl.thumbnail.processors import dynamic_import
from sorl.thumbnail import defaults


def get_thumbnail_setting(setting, override=None):
    """
    Get a thumbnail setting from Django settings module, falling back to the
    default.

    If override is not None, it will be used instead of the setting.
    """
    if override is not None:
        return override
    if hasattr(settings, 'THUMBNAIL_%s' % setting):
        return getattr(settings, 'THUMBNAIL_%s' % setting)
    else:
        return getattr(defaults, setting)


class DjangoThumbnail(Thumbnail):
    def __init__(self, relative_source, requested_size, opts=None,
                 quality=None, basedir=None, subdir=None, prefix=None,
                 relative_dest=None, processors=None, extension=None):
        relative_source = force_unicode(relative_source)
        # Set the absolute filename for the source file
        source = self._absolute_path(relative_source)

        quality = get_thumbnail_setting('QUALITY', quality)
        convert_path = get_thumbnail_setting('CONVERT')
        wvps_path = get_thumbnail_setting('WVPS')
        if processors is None:
            processors = dynamic_import(get_thumbnail_setting('PROCESSORS'))

        # Call super().__init__ now to set the opts attribute. generate() won't
        # get called because we are not setting the dest attribute yet.
        super(DjangoThumbnail, self).__init__(source, requested_size,
            opts=opts, quality=quality, convert_path=convert_path,
            wvps_path=wvps_path, processors=processors)

        # Get the relative filename for the thumbnail image, then set the
        # destination filename
        if relative_dest is None:
            self.relative_dest = \
               self._get_relative_thumbnail(relative_source, basedir=basedir,
                                            subdir=subdir, prefix=prefix,
                                            extension=extension)
        else:
            self.relative_dest = relative_dest
        self.dest = self._absolute_path(self.relative_dest)

        # Call generate now that the dest attribute has been set
        self.generate()

        # Set the relative & absolute url to the thumbnail
        self.relative_url = \
            iri_to_uri('/'.join(self.relative_dest.split(os.sep)))
        self.absolute_url = '%s%s' % (settings.MEDIA_URL, self.relative_url)

    def _get_relative_thumbnail(self, relative_source,
                                basedir=None, subdir=None, prefix=None,
                                extension=None):
        """
        Returns the thumbnail filename including relative path.
        """
        basedir = get_thumbnail_setting('BASEDIR', basedir)
        subdir = get_thumbnail_setting('SUBDIR', subdir)
        prefix = get_thumbnail_setting('PREFIX', prefix)
        extension = get_thumbnail_setting('EXTENSION', extension)
        path, filename = os.path.split(relative_source)
        basename, ext = os.path.splitext(filename)
        name = '%s%s' % (basename, ext.replace(".", "_"))
        size = '%sx%s' % tuple(self.requested_size)

        opts = self.opts and ('%s_' % '_'.join(self.opts)) or ''
        extension = extension and '.%s' % extension
        thumbnail_filename = '%s%s_%s_%sq%s%s' % (prefix, name, size,
                                                  opts, self.quality,
                                                  extension)
        return os.path.join(basedir, path, subdir, thumbnail_filename)

    def _absolute_path(self, filename):
        absolute_filename = os.path.join(settings.MEDIA_ROOT, filename)
        return absolute_filename.encode(settings.FILE_CHARSET)

    def __unicode__(self):
        return self.absolute_url
