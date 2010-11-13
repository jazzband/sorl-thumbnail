from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class, tokey, serialize
from sorl.thumbnail.parsers import parse_geometry
from sorl.thumbnail.images import ImageFile


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

    extensions = {
        'JPEG': 'jpg',
        'PNG': 'png',
    }

    def __init__(self, engine=None, kvstore=None, storage=None):
        if engine is None:
            engine = get_module_class(settings.THUMBNAIL_ENGINE)()
        if kvstore is None:
            kvstore = get_module_class(settings.THUMBNAIL_KVSTORE)()
        if storage is None:
            storage = get_module_class(settings.THUMBNAIL_STORAGE)()
        self.engine = engine
        self.kvstore = kvstore
        self.storage = storage

    def get_thumbnail(self, file_, geometry_string, **options):
        """
        Returns thumbnail as an ImageFile instance for file with geometry and
        options given. First it will try to get it from the key value store,
        secondly it will create it.
        """
        source = ImageFile(file_)
        for key, value in self.default_options.iteritems():
            options.setdefault(key, value)
        name = self._get_thumbnail_filename(source, geometry_string, options)
        thumbnail = ImageFile(name, self.storage)
        cached = self.kvstore.get(thumbnail)
        if cached:
            return cached
        if not thumbnail.exists():
            # We have to check exists() because the Storage backend does not
            # overwrite in some implementations.
            self._create_thumbnail(source, geometry_string, options, thumbnail)
        # If the thumbnail exists we don't do anything, the other option is to
        # delete and write but this could lead to race conditions so I will
        # just leave that out for now.
        self.kvstore.set(thumbnail, source)
        return thumbnail

    def _create_thumbnail(self, source, geometry_string, options, thumbnail):
        """
        Creates the thumbnail by using self.engine and stores the source to
        kvstore if its not already there.
        """
        source_image = self.engine.get_image(source)
        source_image_ratio = self.engine.get_image_ratio(source_image)
        if not self.kvstore.get(source):
            # We store the source in kvstore if its not there already. The
            # reason for us doing that here is because we have the file open
            # and can cheaply access size.
            source_image_size = self.engine.get_image_size(source_image)
            source.set_size(source_image_size)
            self.kvstore.set(source)
        geometry = parse_geometry(geometry_string, source_image_ratio)
        thumbnail_image = self.engine.create(source_image, geometry, options)
        self.engine.write(thumbnail_image, options, thumbnail)
        # It's much cheaper to set the size here too
        thumbnail_image_size = self.engine.get_image_size(thumbnail_image)
        thumbnail.set_size(thumbnail_image_size)

    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        key = tokey(source.key, geometry_string, serialize(options))
        # make some subdirs
        path = '%s/%s/%s' % (key[:2], key[2:4], key)
        return '%s%s.%s' % (settings.THUMBNAIL_PREFIX, path,
                            self.extensions[options['format']])

