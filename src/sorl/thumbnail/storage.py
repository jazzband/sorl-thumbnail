import re
import urllib2
from abc import ABCMeta, abstractmethod, abstractproperty
from django.core.files.base import File, ContentFile
from django.core.files.storage import Storage, FileSystemStorage
from django.utils.encoding import force_unicode
from django.utils import simplejson
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import ThumbnailError, tokey, get_module_class


url_pat = re.compile(r'^(https?|ftp):\/\/')


def serialize_image_file(image_file):
    if image_file.size is None:
        raise ThumbnailError('Trying to serialize ImageFile ``%s`` with size'
                             '``None``' % image_file.name)
    data = {
        'name': image_file.name,
        'storage': image_file.serialize_storage(),
        'size': image_file.size,
    }
    return simplejson.dumps(data)


def deserialize_image_file(s):
    data = simplejson.loads(s)
    storage = get_module_class(data['storage'])()
    image_file = ImageFile(data['name'], storage)
    image_file.size = data['size']
    return image_file


class ImageFile(object):
    size = None

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

    def __unicode__(self):
        return self.name

    def exists(self):
        return self.storage.exists(self.name)

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

    def delete(self):
        return self.storage.delete(self.name)

    def serialize_storage(self):
        cls = self.storage.__class__
        return '%s.%s' % (cls.__module__, cls.__name__)

    @property
    def key(self):
        return tokey(self.name, self.serialize_storage())

    def serialize(self):
        return serialize_image_file(self)


class UrlStorage(Storage):
    def open(self, name):
        return urllib2.urlopen(name, timeout=settings.THUMBNAIL_URL_TIMEOUT)

    def url(self, name):
        return name

    def delete(self, name):
        pass

