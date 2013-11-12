import django

__all__ = ['json', 'BufferIO']

if django.VERSION <= (1, 5):
    from django.utils import simplejson as json
else:
    import json

try:
    from io import BytesIO as BufferIO
except ImportError:
    from cStringIO import StringIO as BufferIO
