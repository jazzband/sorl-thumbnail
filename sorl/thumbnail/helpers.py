import hashlib
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str
from django.utils.importlib import import_module
from django.utils import simplejson


class ThumbnailError(Exception):
    pass


class SortedJSONEncoder(simplejson.JSONEncoder):
    """
    A json encoder that sorts the dict keys
    """
    def __init__(self, **kwargs):
        kwargs['sort_keys'] = True
        super(SortedJSONEncoder, self).__init__(**kwargs)


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
    return simplejson.dumps(obj, cls=SortedJSONEncoder)


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

