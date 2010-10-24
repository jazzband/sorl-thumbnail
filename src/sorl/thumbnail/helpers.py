import hashlib
import re
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_unicode
from django.utils.importlib import import_module
from sorl.thumbnail.conf import settings
from sorl.thumbnail.storage import UrlStorage


geometry_pat = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?$')


class ThumbnailError(Exception):
    pass

class GeometryParseError(ThumbnailError):
    pass


class Geometry(object):
    """
    Object to represent geometry
    """
    x = None
    y = None

    def __init__(self, geometry_string):
        m = geometry_pat.match(geometry_string)
        def syntax_error():
            return GeometryParseError('Geometry string does not have the '
                    'correct syntax: %s' % geometry_string)
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
        self.x = x
        self.y = y

    width = property(lambda self: self.x)
    height = property(lambda self: self.y)

    def css_margin(self):
        if self.x is not None and self.y is not None:
            margin = [0, 0, 0, 0]
            ex = self.x - self.x
            margin[3] = ex / 2
            marign[1] = ex / 2
            if ex % 2:
                marign[1] += 1
            ey = self.y - self.y
            margin[0] = ex / 2
            marign[2] = ex / 2
            if ex % 2:
                marign[2] += 1
            return ' '.join(map(str, marign))
        else:
            return 'auto'

    def __unicode__(self):
        result = []
        if self.x is not None:
            result.append(unicode(self.x))
        if self.y is not None:
            result.append('x')
            result.append(unicode(self.y))
        return u''.join(result)


class Options(object):
    """
    Wrapper for thumbnail geometry specification and kwargs which also sets
    some defaults if not set.
    """
    defaults = {
        'format': settings.THUMBNAIL_FORMAT,
        'quality': settings.THUMBNAIL_QUALITY,
    }

    def __init__(self, landscape_string, portrait_string, **kwargs):
        self.landscape = Geometry(landscape_string)
        self.portrait = Geometry(portrait_string)
        for key, value in self.defaults.iteritems():
            kwargs.setdefault(key, value)
        self.kwargs = kwargs

    def __unicode__(self):
        result = []
        keys = sorted(self.kwargs.keys())
        for key in keys:
            result.append('%s=%s' % (key, force_unicode(self.kwargs[key])))
        return u'%s %s %s' % (self.landscape, self.portrait, ', '.join(result))


def rndint(number):
    """
    Helper to return best int for a float or just the int it self.
    """
    if isinstance(number, float):
        number = round(number, 0)
    return int(number)


def get_cache_key(*args):
    return '%s%s' % (settings.THUMBNAIL_CACHE_PREFIX, mkhash(*args))


def mkhash(*args):
    """
    Computes a (hopefully :D) unique key from arguments given.
    """
    salt = '-'.join([force_unicode(arg) for arg in args])
    hash_ = hashlib.md5(salt)
    return hash_.hexdigest()


def get_module_class(class_path):
    """
    imports and returns a module class from ``path.to.module.Class``
    argument
    """
    try:
        mod_name, cls_name = attr_path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing module %s: "%s"' %
                                   (mod_name, e)))
    return getattr(mod, cls_name)

