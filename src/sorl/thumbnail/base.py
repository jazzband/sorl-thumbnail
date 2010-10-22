from django.utils.importlib import import_module
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import Options, SimpleFile
from sorl.thumbnail.models import Thumbnail


def get_thumbnailfile(input_file, geometry_string, **kwargs):
    fobj = SimpleFile(input_file)
    mod = import_module(settings.THUMBNAIL_BACKEND)
    backend = mod.ThumbnailBackend(fobj)
    options = Options(geometry_string, kwargs)
    try:
        data = Thumbnail.data.get(fobj.name, fobj.storage_string,
                                  unicode(options))
    except Thumbnail.DoesNotExist:
        if settings.THUMBNAIL_DUMMY:
            # TODO
            pass
        else:
            name = backend.get_filename(options, options.kwargs['format'])
            storage_cls = import_module(settings.THUMBNAIL_FILE_STORAGE)
            storage = storage_cls()
            backend.process(unicode(options.geometry), **options.kwargs)
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
    x = width
    y = height

