from abc import ABCMeta, abstractmethod, abstractproperty
from sorl.thumbnail.conf import settings
from sorl.thumbnail.files import Image


class ThumbnailBackendBase(object):
    __metaclass__ = ABCMeta

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

    def get_thumbnail(self, file_, geometry_string, options,
                      engine=None, storage=None):
        if engine is None:
            engine = get_module_class(settings.THUMBNAIL_ENGINE)()
        if storage is None:
            storage = get_module_class(settings.THUMBNAIL_STORAGE)()
        source = Image(file_)
        for key, value in self.default_options.iteritems():
            options.setdefault(key, value)

        name = self._get_thumbnail_filename(source, geometry_string, options)
        thumbnail = self._get_thumbnail(name)
        if thumbnail is not None:
            return thumbnail
        thumbnail = Image(name, storage)
        if thumbnail.exists():
            # For now we return it, the other option is to overwrite
            # but this could lead to race conditions so I will just
            # leave that out for now
            return thumbnail
        image = self.engine.get_image(source)
        x_image, y_image = self.engine.get_image_size(image)
        geometry = parse_geometry(geometry_string, (x_image, y_image))
        thumbnail_image = self.engine.create(image, geometry, options)
        self.engine.write(thumbnail_image, options, thumbnail)
        # its much cheaper to set the size here since we probably have the
        # image in memory
        thumbnail.size = self.engine.get_image_size(thumbnail_image)
        self._set_thumbnail(source, thumbnail)
        return thumbnail

    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        key = tokey(source.name, source.storage_path, geometry_string,
                    dict_serialize(options))
        # make some subdirs
        path = '%s/%s/%s' % (key[:2], key[2:4], key)
        return '%s%s.%s' % (settings.THUMBNAIL_PREFIX, path,
                            self.extensions[options['format']])
    @abstractmethod
    def _get_thumbnail(self):
        raise NotImplemented()

    @abstractmethod
    def get_image_size(self, image):
        raise NotImplemented()

    def invalidate_cache(self, file_)
        raise NotImplemented()


