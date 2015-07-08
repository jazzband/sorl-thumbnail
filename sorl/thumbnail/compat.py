from __future__ import unicode_literals

import sys

import django

__all__ = [
    'json',
    'BufferIO',
    'urlopen',
    'urlparse',
    'quote',
    'quote_plus',
    'URLError',
    'get_cache',
    'force_unicode', 'text_type'
]

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

# Django version

if django.VERSION < (1, 5):
    from django.utils import simplejson as json
    from django.utils.encoding import force_unicode
else:
    import json
    from django.utils.encoding import force_text as force_unicode

if django.VERSION >= (1, 7):
    from django.core.cache import caches

    get_cache = lambda cache_name: caches[cache_name]
else:
    from django.core.cache import get_cache

try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text

try:
    # Python >= 2.7
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

if django.VERSION >= (1, 7):
    from django.core.cache import caches
    def get_cache(name):
        return caches[name]
else:
    from django.core.cache import get_cache

try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict


# Python 2 and 3

if PY3:
    from urllib.error import URLError
    from urllib.request import urlopen
    from urllib.parse import quote, quote_plus

    import urllib.parse as urlparse

    from io import BytesIO as BufferIO

    text_type = str
    string_type = str


    def encode(value, charset='utf-8', errors='ignore'):
        if isinstance(value, bytes):
            return value
        return value.encode(charset, errors)


    def urlsplit(url):
        return urlparse.urlsplit(url.decode('ascii', 'ignore'))

elif PY2:
    from urllib2 import URLError
    from urllib2 import urlopen
    from urllib import quote, quote_plus

    import urlparse

    from cStringIO import StringIO as BufferIO

    text_type = unicode
    string_type = basestring
    urlsplit = urlparse.urlsplit


    def encode(value, charset='utf-8', errors='ignore'):
        if isinstance(value, unicode):
            return value.encode(charset, errors)
        return unicode(value, errors=errors).encode(charset)
