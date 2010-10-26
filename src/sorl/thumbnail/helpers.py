import hashlib
import re
from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.importlib import import_module
from django.utils import simplejson
from sorl.thumbnail.conf import settings


geometry_pat = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?$')


class ThumbnailError(Exception):
    pass


class GeometryParseError(ThumbnailError):
    pass


def get_thumbnail(file_, geometry, **options):
    """
    Simple function to get a ``sorl.thumbnail.backends.*.Thumbnail`` instance
    """
    thumbnail_cls = get_module_class(settings.THUMBNAIL_BACKEND)
    return thumbnail_cls(file_, geometry, options)


def parse_geometry(geometry):
    """
    Parses a geometry string syntax and returns a (width, height) tuple
    """
    m = geometry_pat.match(geometry)
    def syntax_error():
        return GeometryParseError('Geometry does not have the correct '
                'syntax: %s' % geometry)
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
    return x, y


def dict_serialize(dict_):
    """
    Serializes a dict to JSON format while sorting the keys
    """
    result = SortedDict()
    for key in sorted(dict_.keys()):
        result[key]= dict_[key]
    return simplejson.dumps(result)


def toint(number):
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
        mod_name, cls_name = class_path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing module %s: "%s"' %
                                   (mod_name, e)))
    return getattr(mod, cls_name)

