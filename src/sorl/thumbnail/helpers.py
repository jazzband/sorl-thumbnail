import re
import hashlib
from django.core.files import File
from django.utils.encoding import force_unicode
from django.core.files.storage import FileSystemStorage
from sorl.thumbnail.storage import UrlStorage
from sorl.thumbnail.conf import settings


geometry_pat = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?(?P<modifiers>[\^!><]*)$')
url_pat = re.compile(r'^(https?|ftp):\/\/')


class ThumbnailError(Exception):
    pass

class GeometryParseError(ThumbnailError):
    pass


class Geometry(object):
    """
    Object to represent geometry according to the `GraphicsMagick geometry
    specification
    <http://www.graphicsmagick.org/GraphicsMagick.html#details-geometry`_
    """
    x = None
    y = None
    modifiers = []

    def __init__(self, geometry_string):
        m = geometry_pat.match(geometry_string)
        def syntax_error():
            return GeometryParseError('geometry does not have the correct syntax.')
        if not m:
            raise syntax_error()
        x = m.group('x')
        y = m.group('y')
        if x is None and y is None:
            raise syntax_error()
        if x is not None:
            x = int(x)
        if y is not None:
            y = int(y)
        modifiers = m.group('modifiers')
        if modifiers:
            modifiers = set(modifiers)
        else:
            modifiers = set()
        self.x = x
        self.y = y
        self.modifiers

    def __unicode__(self):
        result = []
        if self.x is not None:
            result.append(self.x)
        if self.y is not None:
            result.append('x')
            result.append(self.y)
        if self.modifiers:
            result.extend(sorted(list(self.modifiers)))
        return u''.join(result)


class Options(object):
    """
    Wrapper for thumbnail geometry specification and kwargs which also sets
    some defaults if not set.
    """
    defaults = {
        'format': settings.THUMNBAIL_FORMAT,
        'quality': settings.THUMBNAIL_QUALITY,
    }

    def __init__(self, geometry_string, kwargs):
        self.geometry = Geometry(geometry_string)
        for key, value in self.defaults.iteritems():
            kwargs.setdefault(key, value)
        self.kwargs = kwargs

    def __unicode__(self):
        result = []
        keys = sorted(self.kwargs.keys())
        for key in keys:
            result.append('%s=%s' % (key, force_unicode(self.kwargs[key])))
        return '%s %s' % (self.geometry, ', '.join(result))


class SimpleFile(object):
    """
    A very simple read-only file wrapper
    """
    def __init__(self, input_file):
        if not input_file:
            raise ThumbnailError('Source is empty.')
        if hasattr(input_file, '__class__') and\
                issubclass(input_file.__class__, File):
            self.name = input_file.name
            self.storage = input_file.storage
        else:
            self.name = force_unicode(input_file)
            m = url_pat.match(self.name)
            if m:
                self.storage = UrlStorage()
            else:
                self.storage = FileSystemStorage()

    def read(self):
        return self.storage.read(self.name)

    @property
    def storage_string(self):
        """
        Returns the storage instance string representation.
        """
        cls = self.storage.__class__
        return '%s.%s' % (cls.__module__, cls.__name__)


def get_unique_key(*args):
    """
    Computes a (hopefully :D) unique key from arguments given.
    """
    salt = '-'.join([force_unicode(arg) for arg in args])
    hash_ = hashlib.md5(salt)
    return hash_.hexdigest()

