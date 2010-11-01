import re
import urllib2
from abc import ABCMeta, abstractmethod, abstractproperty
from django.core.files.base import File, ContentFile
from django.core.files.storage import Storage, FileSystemStorage
from django.utils.encoding import force_unicode
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import ThumbnailError, get_thumbnail_engine


url_pat = re.compile(r'^(https?|ftp):\/\/')


class Image(object):
    _size = None

    def __init__(self, file_, storage=None):
        if not file_:
            raise ThumbnailError('File is empty.')
        # figure out name
        if hasattr(file_, 'name'):
            self.name = file_.name
        else:
            self.name = force_unicode(file_)
        # figure out storage
        if storage is not None:
            self.storage = storage
        elif hasattr(file_, 'storage'):
            self.storage = file_.storage
        else:
            if url_pat.match(self.name):
                self.storage = UrlStorage()
            else:
                self.storage = FileSystemStorage()

    def exists(self):
        return self.storage.exists(self.name)

    def _get_size(self):
        if self._size is None:
            # Test if the storage has an `image_size` attribute Storage class can
            # implement this for a more efficient way to get the image size.
            if hasattr(self.storage, 'image_size'):
                self._size = self.storage.image_size(self.name)
            else:
                # This is the worst case scenario, we probably need to read the
                # file contents into memory depending on the engine implementation
                engine = get_module_class(settings.THUMBNAIL_ENGINE)()
                image = engine.get_image(self)
                self._size = engine.get_image_size(image)
        return self._size
    def _set_size(self, size):
        self._size = size
    size = property(_get_size, _set_size)

    @property
    def width(self):
        return self.size[0]
    x = width

    @property
    def height(self):
        return self.size[1]
    y = height

    def is_portrait(self):
        return self.y > self.x

    @property
    def url(self):
        return self.storage.url(self.name)

    def read(self):
        return self.storage.open(self.name).read()

    def write(self, content):
        if not isinstance(content, File):
            content = ContentFile(content)
        self.size = None
        return self.storage.save(self.name, content)

    @property
    def serialized_storage(self):
        cls = self.storage.__class__
        return '%s.%s' % (cls.__module__, cls.__name__)


class UrlStorage(Storage):
    def open(self, name, mode='rb'):
        return urllib2.urlopen(name, timeout=settings.THUMBNAIL_URL_TIMEOUT)

