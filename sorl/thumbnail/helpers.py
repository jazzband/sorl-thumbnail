import hashlib
from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str
from django.utils.importlib import import_module
from django.utils import simplejson


class ThumbnailError(Exception):
    pass


def toint(number):
    """
    Helper to return rounded int for a float or just the int it self.
    """
    if isinstance(number, float):
        number = round(number, 0)
    return int(number)


def tokey(*args):
    """
    Computes a (hopefully) unique key from arguments given.
    """
    salt = '||'.join([smart_str(arg) for arg in args])
    hash_ = hashlib.md5(salt)
    return hash_.hexdigest()


def serialize(obj):
    if isinstance(obj, dict):
        result = SortedDict()
        for key in sorted(obj.keys()):
            result[key]= obj[key]
        obj = result
    return simplejson.dumps(obj)


def deserialize(s):
    return simplejson.loads(s)


def get_module_class(class_path):
    """
    imports and returns module class from ``path.to.module.Class``
    argument
    """
    try:
        mod_name, cls_name = class_path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing module %s: "%s"' %
                                   (mod_name, e)))
    return getattr(mod, cls_name)

