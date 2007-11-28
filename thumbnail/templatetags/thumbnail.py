import re, os
from django.template import Library
from sorl.thumbnail import Thumbnail, METHOD_LIST
from django.conf import settings

register = Library()

@register.filter
def thumbnail_url(filename, arg=""):
    try:
        thumbnail = get_thumbnail(filename, arg)
    except:
        if hasattr(settings, 'THUMBNAIL_DEBUG') and settings.THUMBNAIL_DEBUG:
            raise
        else:
            return ""
    
    return thumbnail.get_url()

def get_thumbnail(filename, arg=""):

    kwargs  = {\
        'prefix': '',
        'subdir': '_thumbs',
        'size': (80,80),
        'quality': 85,
    }

    for a in kwargs.keys():
        if hasattr(settings, 'THUMBNAIL_%s' % a.upper()):
            kwargs.update({a: getattr(settings, 'THUMBNAIL_%s' % a.upper())})
    
    kwargs.update({\
        'filename': filename,
        'crop': False,
        'upscale': False,
        'bw': False,
    }
     
    for m in METHOD_LIST:
        if arg.find(m) != -1:
            kwargs.update({m: True})
    quality_pat = re.compile(r'q(\d+)')
    m = quality_pat.search(arg)
    if m:
        quality = int(m.group(1))
        if quality > 0 and quality <= 100:
            kwargs.update(quality=quality)
    size_pat = re.compile(r'(\d+)x(\d+)')
    m = size_pat.search(arg)
    if m:
        kwargs.update(size=(int(m.group(1)), int(m.group(2))))

    return Thumbnail(**kwargs)
