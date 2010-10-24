from django.utils.importlib import import_module
from django.core.files.storage import get_storage_class
from django.core.exceptions import ImproperlyConfigured
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import Options, ReadOnlyFile, get_module_attr
from sorl.thumbnail.models import Thumbnail


def get_thumbnailfile(input_file, landscape_string, portrait_string=None,
                      **kwargs):
    if portrait_string is None:
        portrait_string = landscape_string
    fobj = ReadOnlyFile(input_file)
    options = Options(landscape_string, portrait_string, **kwargs)
    try:
        data = Thumbnail.data.get(fobj.name, fobj.storage_string,
                                  unicode(options))
    except Thumbnail.DoesNotExist:
        if settings.THUMBNAIL_DUMMY:
            # TODO
            pass
        else:
            backend_cls = get_module_attr(settings.THUMBNAIL_BACKEND)
            backend = backend_cls(fobj)
            name = backend.get_filename(options, **options.kwargs)
            storage_cls = get_module_attr(settings.THUMBNAIL_FILE_STORAGE)
            storage = storage_cls()
            backend.process(options.landscape, options.portrait,
                            **options.kwargs)
            backend.write(name, storage, **options.kwargs)
            obj = Thumbnail.objects.create(
                source_name=fobj.name,
                source_storage=fobj.storage_string,
                name=name,
                url=storage.url(name),
                path=storage.path(name),
                width=backend.width,
                height=backend.height,
                size=storage.size(name),
                )
            data = obj.__dict__
    return ThumbnailFile(data)


class ThumbnailFile(object):
    def __init__(self, data):
        self.data = data

    name = property(lambda self: self.data['name'])
    url = property(lambda self: self.data['url'])
    path = property(lambda self: self.data['path'])
    width = property(lambda self: self.data['width'])
    height = property(lambda self: self.data['height'])
    size = property(lambda self: self.data['size'])
    landscape = property(lambda self: self.x >= self.y)
    portrait = property(lambda self: self.y >= self.x)
    # TODO
    margin = property(lambda self: None)
    x = width
    y = height

