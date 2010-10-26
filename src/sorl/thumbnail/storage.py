from django.core.files.base import File, ContentFile
from django.core.files.storage import Storage, FileSystemStorage
from django.utils.encoding import force_unicode
from sorl.thumbnail.conf import settings
import re
import urllib2


url_pat = re.compile(r'^(https?|ftp):\/\/')


class StorageImage(object):
    _dimensions = None # dimensions cache

    def __init__(self, file_, storage=None):
        if not file_:
            raise ValueError('File is empty.')
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
            # Using PIL although it should not be a requirement, hence
            # the local import until I figure out i I want to keep this at all
            from cStringIO import StringIO
            from PIL import Image
            buf = StringIO(self.open().read())
            im = Image.open(buf)
            self._dimensions = im.size
            buf.close()
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

