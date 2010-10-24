import re
import urllib2
from cStringIO import StringIO
from PIL import Image
from django.core.files.storage import Storage
from django.core.files.base import File, ContentFile
from sorl.thumbnail.conf import settings


url_pat = re.compile(r'^(https?|ftp):\/\/')


class StorageImage(object):
    def __init__(self, file_):
        self._dimensions = None # dimensions cache
        if not file_:
            raise ThumbnailError('File is empty.')
        if hasattr(file_, 'name'):
            self.name = name
        else:
            self.name = force_unicode(_file)
        if hasattr(file_, 'storage'):
            self.storage = file_.storage
        else:
            if url_pat.match(self.name):
                self.storage = UrlStorage()
            else:
                self.storage = FileSystemStorage()

    @property
    def exists(self):
        return self.storage.exists(self.name)

    @property
    def path(self):
        return self.storage.path(self.name)

    @property
    def accessed_time(self):
        return self.storage.accessed_time(self.name)

    @property
    def created_time(self):
        return self.storage.created_time(self.name)

    @property
    def modified_time(self):
        return self.storage.modified_time(self.name)

    @property
    def size(self):
        return self.storage.size(self.name)

    @property
    def dimensions(self):
        if self._dimensions is None:
            # XXX Loading the whole source into memory, eeeks
            buf = StringIO(self.open().read())
            im = Image.open(buf)
            self._dimensions = im.size
        return self._dimensions

    @property
    def width(self):
        return self.dimensions[0]
    x = width

    @property
    def height(self):
        return self.dimensions[1]
    y = height

    def is_portrait(self):
        return self.y > self.x

    @property
    def url(self):
        return self.storage.url(self.name)

    def open(self, mode='rb'):
        return self.storage.open(self.name, mode=mode)

    def read(self):
        return self.open().read()

    def save(self, content):
        if not isinstance(content, File):
            content = ContentFile(content)
        self._dimensions = None # reset the dimensions cache
        return self.storage.save(self.name, content)

    def delete(self):
        return self.storage.delete(self.name)

    @property
    def storage_path(self):
        cls = self.storage.__class__
        return '%s.%s' % (cls.__module__, cls.__name__)


class UrlStorage(Storage):
    def open(self, name, *args, **kwargs):
        return urllib2.urlopen(name, timeout=settings.THUMBNAIL_URL_TIMEOUT)

