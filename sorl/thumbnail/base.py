import re

from sorl.thumbnail.conf import settings, defaults as default_settings
from sorl.thumbnail.helpers import tokey, serialize
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail import default
from sorl.thumbnail.parsers import parse_geometry

import logging

logger = logging.getLogger(__name__)

EXTENSIONS = {
    'JPEG': 'jpg',
    'PNG': 'png',
}


class ThumbnailBackend(object):
    """
    The main class for sorl-thumbnail, you can subclass this if you for example
    want to change the way destination filename is generated.
    """

    default_options = {
        'format': settings.THUMBNAIL_FORMAT,
        'quality': settings.THUMBNAIL_QUALITY,
        'colorspace': settings.THUMBNAIL_COLORSPACE,
        'upscale': settings.THUMBNAIL_UPSCALE,
        'crop': False,
        'cropbox': None,
        'rounded': None,
    }

    extra_options = (
        ('progressive', 'THUMBNAIL_PROGRESSIVE'),
        ('orientation', 'THUMBNAIL_ORIENTATION'),
        ('blur', 'THUMBNAIL_BLUR'),
    )

    file_extension = lambda inst, file_: str(file_).split('.')[-1].lower()

    def _get_format(self, file_):
        file_extension = self.file_extension(file_)

        is_jpeg = re.match('jpg|jpeg', file_extension)
        is_png = re.match('png', file_extension)

        if is_jpeg:
            format_ = 'JPEG'
        elif is_png:
            format_ = 'PNG'
        else:
            format_ = default_settings.THUMBNAIL_FORMAT

        return str(format_)

    def get_thumbnail(self, file_, geometry_string, **options):
        """
        Returns thumbnail as an ImageFile instance for file with geometry and
        options given. First it will try to get it from the key value store,
        secondly it will create it.
        """
        logger.debug('Getting thumbnail for file [%s] at [%s]', file_,
                     geometry_string)
        source = ImageFile(file_)

        #preserve image filetype
        if settings.THUMBNAIL_PRESERVE_FORMAT:
            self.default_options['format'] = self._get_format(file_)

        for key, value in self.default_options.iteritems():
            options.setdefault(key, value)
            # For the future I think it is better to add options only if they
        # differ from the default settings as below. This will ensure the same
        # filenames beeing generated for new options at default.
        for key, attr in self.extra_options:
            value = getattr(settings, attr)
            if value != getattr(default_settings, attr):
                options.setdefault(key, value)
        name = self._get_thumbnail_filename(source, geometry_string, options)
        thumbnail = ImageFile(name, default.storage)
        cached = default.kvstore.get(thumbnail)
        if cached:
            return cached
        else:
            # We have to check exists() because the Storage backend does not
            # overwrite in some implementations.
            # so we make the assumption that if the thumbnail is not cached, it doesn't exist
            try:
                source_image = default.engine.get_image(source)
            except IOError:
                # if S3Storage says file doesn't exist remotely, don't try to
                # create it, exit early
                # Will return working empty image type; 404'd image
                logger.warn('Remote file [%s] at [%s] does not exist', file_,
                            geometry_string)
                return thumbnail
                # We might as well set the size since we have the image in memory
            size = default.engine.get_image_size(source_image)
            source.set_size(size)
            self._create_thumbnail(source_image, geometry_string, options,
                                   thumbnail)
            # If the thumbnail exists we don't create it, the other option is
        # to delete and write but this could lead to race conditions so I
        # will just leave that out for now.
        default.kvstore.get_or_set(source)
        default.kvstore.set(thumbnail, source)
        return thumbnail

    def delete(self, file_, delete_file=True):
        """
        Deletes file_ references in Key Value store and optionally the file_
        it self.
        """
        image_file = ImageFile(file_)
        if delete_file:
            image_file.delete()
        default.kvstore.delete(image_file)

    def _create_thumbnail(self, source_image, geometry_string, options,
                          thumbnail):
        """
        Creates the thumbnail by using default.engine
        """
        logger.debug('Creating thumbnail file [%s] at [%s] with [%s]',
                     thumbnail.name, geometry_string, options)
        ratio = default.engine.get_image_ratio(source_image, options)
        geometry = parse_geometry(geometry_string, ratio)
        image = default.engine.create(source_image, geometry, options)
        default.engine.write(image, options, thumbnail)
        # It's much cheaper to set the size here
        size = default.engine.get_image_size(image)
        thumbnail.set_size(size)

    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        key = tokey(source.key, geometry_string, serialize(options))
        # make some subdirs
        path = '%s/%s/%s' % (key[:2], key[2:4], key)
        return '%s%s.%s' % (settings.THUMBNAIL_PREFIX, path,
                            EXTENSIONS[options['format']])

