import re, os
from django.template import Library
from sorl.thumbnail.main import Thumbnail
from django.conf import settings

register = Library()

@register.filter
def thumbnail_url(filename, arg=""):
    try:
        thumbnail = get_thumbnail(filename, arg)
    except:
        if debug():
            raise
        else:
            return ""
    
    return thumbnail.get_url()

def debug():
    return hasattr(settings, 'THUMBNAIL_DEBUG') and settings.THUMBNAIL_DEBUG

def get_thumbnail(filename, arg=""):

    kwargs = {'filename': filename, 'options': arg.split()}
    attr = ['prefix', 'subdir', 'quality', 'filename_encoding']
    for a in attr:
        if hasattr(settings, 'THUMBNAIL_%s' % a.upper()):
            kwargs.update({a: getattr(settings, 'THUMBNAIL_%s' % a.upper())})
     
    quality_pat = re.compile(r'q(\d+)')
    m = quality_pat.search(arg)
    if m:
        quality = int(m.group(1))
    size_pat = re.compile(r'(\d+)x(\d+)')
    m = size_pat.search(arg)
    if m:
        kwargs.update(size=(int(m.group(1)), int(m.group(2))))

    return Thumbnail(**kwargs)
