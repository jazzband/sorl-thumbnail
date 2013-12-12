import sys

import django

__all__ = [
    'json',
    'BufferIO',
    'urlopen', 'URLError',
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


# Python 2 and 3

if PY3:
    from urllib.request import urlopen
    from urllib.error import URLError

    from io import BytesIO as BufferIO

    text_type = str

    def encode(value):
        return value.encode('utf-8')

elif PY2:
    from urllib2 import URLError
    from urllib import urlopen

    from cStringIO import StringIO as BufferIO

    text_type = unicode

    def encode(value):
        return unicode(value, errors='ignore').encode('utf-8')
