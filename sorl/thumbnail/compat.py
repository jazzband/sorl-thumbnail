import django
import sys

__all__ = ['json', 'BufferIO', 'urlopen', 'URLError']
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if django.VERSION <= (1, 5):
    from django.utils import simplejson as json
else:
    import json

try:
    from io import BytesIO as BufferIO
except ImportError:
    from cStringIO import StringIO as BufferIO

try:
    if PY3:
        from urllib.request import urlopen
        from urllib.error import URLError
    else:
        from urllib import URLError
        from urllib import urlopen
except ImportError:
    #For python2
    from urllib2 import URLError
    from urllib2 import urlopen


if PY3:
    text_type = str
else:
    text_type = unicode
