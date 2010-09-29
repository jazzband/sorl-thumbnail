import urllib2
from django.core.files import File
from django.core.files.storage import Storage
from sorl.thumbnail.conf import settings


class UrlStorage(Storage):
    def open(self, name, *args, **kwargs):
        fp = urllib2.urlopen(name, timeout=settings.THUMBNAIL_URL_TIMEOUT)
        return File(fp, name)

