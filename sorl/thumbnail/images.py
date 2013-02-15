import re
import urllib2
from hashlib import md5
from django.core.files.base import File, ContentFile
from django.core.files.storage import Storage, default_storage
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.utils.functional import LazyObject, cached_property
from django.utils import simplejson
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import ThumbnailError, tokey, get_module_class
from sorl.thumbnail import default
from sorl.thumbnail.parsers import parse_geometry

url_pat = re.compile(r'^(https?|ftp):\/\/')


def serialize_image_file(image_file):
    if image_file.size is None:
        raise ThumbnailError('Trying to serialize an ``ImageFile`` with a '
                             '``None`` size.')
    data = {
        'name': image_file.name,
        'storage': image_file.serialize_storage(),
        'size': image_file.size,
    }
    return simplejson.dumps(data)


def deserialize_image_file(s):
    data = simplejson.loads(s)
    class LazyStorage(LazyObject):
        def _setup(self):
            self._wrapped = get_module_class(data['storage'])()
    image_file = ImageFile(data['name'], LazyStorage())
    image_file.set_size(data['size'])
    return image_file


class BaseImageFile(object):
    def exists(self):
        raise NotImplemented()

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
    def ratio(self):
        return float(self.x) / self.y

    @property
    def url(self):
        raise NotImplemented()
    src = url


class ImageFile(BaseImageFile):
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
        elif url_pat.match(self.name):
            self.storage = UrlStorage()
        else:
            self.storage = default_storage

    @cached_property
    def file_hash(self):
        if self.exists():
            image = default.engine.get_image(self)
            my_hash = md5(image.tostring()).hexdigest()
            return my_hash

        return ''

    def __unicode__(self):
        return self.name

    def exists(self):
        return self.storage.exists(self.name)

    def set_size(self, size=None):
        # set the size if given
        if size is not None:
            pass
        # Don't try to set the size the expensive way if it already has a
        # value.
        elif self._size is not None:
            return
        elif hasattr(self.storage, 'image_size'):
            # Storage backends can implement ``image_size`` method that
            # optimizes this.
            size = self.storage.image_size(self.name)
        else:
            # This is the worst case scenario
            image = default.engine.get_image(self)
            size = default.engine.get_image_size(image)
        self._size = list(size)

    @property
    def size(self):
        return self._size

    @cached_property
    def url(self):
        return self.storage.url(self.name)

    def read(self):
        return self.storage.open(self.name).read()

    def write(self, content):
        if not isinstance(content, File):
            content = ContentFile(content)
        self._size = None
        return self.storage.save(self.name, content)

    def delete(self):
        return self.storage.delete(self.name)

    def serialize_storage(self):
        if isinstance(self.storage, LazyObject):
            # if storage is wrapped in a lazy object we need to get the real
            # thing.
            self.storage._setup()
            cls = self.storage._wrapped.__class__
        else:
            cls = self.storage.__class__
        return '%s.%s' % (cls.__module__, cls.__name__)

    @cached_property
    def key(self):
        return tokey(self.name, self.file_hash, self.serialize_storage())

    def serialize(self):
        return serialize_image_file(self)


class DummyImageFile(BaseImageFile):
    def __init__(self, geometry_string):
        self.size = parse_geometry(
            geometry_string,
            settings.THUMBNAIL_DUMMY_RATIO,
            )

    def exists(self):
        return True

    @property
    def url(self):
        return settings.THUMBNAIL_DUMMY_SOURCE % (
            {'width': self.x, 'height': self.y}
            )


class UrlStorage(Storage):
    def open(self, name):
        return urllib2.urlopen(name)

    def exists(self, name):
        try:
            self.open(name)
        except urllib2.URLError:
            return False
        return True

    def url(self, name):
        return name

    def delete(self, name):
        pass

