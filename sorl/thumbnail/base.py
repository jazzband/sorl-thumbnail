from sorl.thumbnail.conf import settings, defaults as default_settings
from sorl.thumbnail.helpers import tokey, serialize
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail import default
from sorl.thumbnail.parsers import parse_geometry

from copy import copy


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
    }

    extra_options = (
        ('progressive', 'THUMBNAIL_PROGRESSIVE'),
        ('orientation', 'THUMBNAIL_ORIENTATION'),
    )

    def get_thumbnail(self, file_, geometry_string, **options):
        """
        Returns thumbnail as an ImageFile instance for file with geometry and
        options given. First it will try to get it from the key value store,
        secondly it will create it.
        """
        source = ImageFile(file_)
        options = self._get_options(options)
        name = self._get_thumbnail_filename(source, geometry_string, options)
        thumbnail = ImageFile(name, default.storage)

        cached = default.kvstore.get(thumbnail)
        if cached:
            return cached
        if not thumbnail.exists():
            # We have to check exists() because the Storage backend does not
            # overwrite in some implementations.
            thumbnail = self.handle_thumbnail(source, thumbnail,
                                              geometry_string, options)
        else:
            # If the thumbnail exists we don't create it, the other option is
            # to delete and write but this could lead to race conditions so I
            # will just leave that out for now.
            default.kvstore.set(source)
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

    def handle_thumbnail(self, source, thumbnail, geometry_string, options):
        """
        Handle thumbnail creation. Subclasses can override this method to
        change behavior (e.g., return a dummy ImageFile and offload thumbnail
        processing to a job queue).
        """
        source, thumbnail = copy(source), copy(thumbnail)
        source, thumbnail = self._write_thumbnail(source, thumbnail,
                                                  geometry_string, options)
        # If we arrived here it's safe to cache metadata on kvstore
        default.kvstore.set(source)
        default.kvstore.set(thumbnail, source)
        return thumbnail

    def _write_thumbnail(self, source, thumbnail, geometry_string, options):
        """
        Write a thumbnail from a source ImageFile using default.engine
        """
        # Load source image
        source_image = default.engine.get_image(source)
        # We might as well set the size since we have the image in memory
        source.set_size(default.engine.get_image_size(source_image))
        # Calculate thumbnail size and ratio
        ratio = default.engine.get_image_ratio(source_image)
        geometry = parse_geometry(geometry_string, ratio)
        # Generate thumbnail
        image = default.engine.create(source_image, geometry, options)
        default.engine.write(image, options, thumbnail)
        # It's much cheaper to set the size here
        size = default.engine.get_image_size(image)
        thumbnail.set_size(size)
        return source, thumbnail

    def _get_options(self, options):
        """
        Get the specified options and set defaults when appropriate.
        """
        for key, value in self.default_options.iteritems():
            options.setdefault(key, value)
        # For the future I think it is better to add options only if they
        # differ from the default settings as below. This will ensure the same
        # filenames beeing generated for new options at default.
        for key, attr in self.extra_options:
            value = getattr(settings, attr)
            if value != getattr(default_settings, attr):
                options.setdefault(key, value)
        return options

    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        key = tokey(source.key, geometry_string, serialize(options))
        # make some subdirs
        path = '%s/%s/%s' % (key[:2], key[2:4], key)
        return '%s%s.%s' % (settings.THUMBNAIL_PREFIX, path,
                            EXTENSIONS[options['format']])

