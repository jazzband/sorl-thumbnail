import os.path
from UserDict import DictMixin

from django.db.models.fields.files import ImageField, ImageFieldFile
from django.utils.safestring import mark_safe
from django.utils.functional import curry
from django.utils.html import escape
from django.conf import settings

from sorl.thumbnail.main import DjangoThumbnail
#from sorl.thumbnail.utils import delete_thumbnails  (TODO:)


REQUIRED_ARGS = ('size',)
ALL_ARGS = {
    'size': 'requested_size',
    'options': 'opts',
    'quality': 'quality',
    'basedir': 'basedir',
    'subdir': 'subdir',
    'prefix': 'prefix',
}
TAG_HTML = '<img src="%(src)s" width="%(width)s" height="%(height)s" alt="" />'


class ThumbsDict(object, DictMixin):
    def __init__(self, descriptor):
        super(ThumbsDict, self).__init__()
        self.descriptor = descriptor

    def keys(self):
        return self.descriptor.field.extra_thumbnails.keys()


class LazyThumbs(ThumbsDict):
    def __init__(self, *args, **kwargs):
        super(LazyThumbs, self).__init__(*args, **kwargs)
        self.cached = {}

    def __getitem__(self, key):
        thumb = self.cached.get(key)
        if not thumb:
            args = self.descriptor.field.extra_thumbnails[key]
            thumb = self.descriptor._build_thumbnail(args)
            self.cached[key] = thumb
        return thumb

    def keys(self):
        return self.descriptor.field.extra_thumbnails.keys()


class ThumbTags(ThumbsDict):
    def __getitem__(self, key):
        thumb = self.descriptor.extra_thumbnails[key]
        return self.descriptor._build_thumbnail_tag(thumb)


class ImageWithThumbnailsFieldFile(ImageFieldFile):
    def _build_thumbnail(self, args):
        # Build kwargs
        kwargs = {}
        for k, v in args.items():
            kwargs[ALL_ARGS[k]] = v
        # Build relative source path
        filename = getattr(self.instance, self.field.name).path
        media_root_len = len(os.path.normpath(settings.MEDIA_ROOT))
        filename = os.path.normpath(filename)
        filename = filename[media_root_len:].lstrip(os.path.sep)
        # Return thumbnail
        return DjangoThumbnail(filename, **kwargs)

    def _build_thumbnail_tag(self, thumb):
        opts = dict(src=escape(thumb), width=thumb.width(),
                    height=thumb.height())
        return mark_safe(self.field.thumbnail_tag % opts)

    def _get_thumbnail(self):
        return self._build_thumbnail(self.field.thumbnail)
    thumbnail = property(_get_thumbnail)

    def _get_extra_thumbnails(self):
        if self.field.extra_thumbnails is None:
            return None
        if not hasattr(self, '_extra_thumbnails'):
            self._extra_thumbnails = LazyThumbs(self)
        return self._extra_thumbnails
    extra_thumbnails = property(_get_extra_thumbnails)

    def _get_thumbnail_tag(self):
        return self._build_thumbnail_tag(self.thumbnail)
    thumbnail_tag = property(_get_thumbnail_tag)

    def _get_extra_thumbnails_tag(self):
        if self.field.extra_thumbnails is None:
            return None
        return ThumbTags(self)
    extra_thumbnails_tag = property(_get_extra_thumbnails_tag)


class ImageWithThumbnailsField(ImageField):
    """
    photo = ImageWithThumbnailsField(
        upload_to='uploads',
        thumbnail={
            'size': (80, 80),
            'options': ('crop', 'upscale'),
        },
        extra_thumbnails={
            'admin': {
                'size': (70, 50),
                'options': ('sharpen',),
            }
        }
    )
    """
    attr_class = ImageWithThumbnailsFieldFile

    def __init__(self, thumbnail, extra_thumbnails=None,
                 thumbnail_tag=TAG_HTML, **kwargs):
        super(ImageWithThumbnailsField, self).__init__(**kwargs)
        _verify_thumbnail_attrs(thumbnail)
        if extra_thumbnails:
            for extra, attrs in extra_thumbnails.items():
                name = "%r of 'extra_thumbnails'"
                _verify_thumbnail_attrs(attrs, name)
        self.thumbnail = thumbnail
        self.extra_thumbnails = extra_thumbnails
        self.thumbnail_tag = thumbnail_tag

    # TODO: saving the file should generate thumbnails.
    #def save_file(self, *args, **kwargs):
    #    super(ImageWithThumbnailField, self).save_file(*args, **kwargs)
    #    _get_thumbnail()

    # TODO: deleting the image should delete its thumbnails too.
    # Note that  http://code.google.com/p/sorl-thumbnail/issues/detail?id=23
    # mentions a problem with using *args, **kwargs, so test that too.
    #def delete_file(self, *args, **kwargs):
    #    super(ImageWithThumbnailField, self).delete_file(*args, **kwargs)
    #    delete_thumbnails()

def _verify_thumbnail_attrs(attrs, name="'thumbnail'"):
    for arg in REQUIRED_ARGS:
        if arg not in attrs:
            raise TypeError('Required attr %r missing in %s arg' % (arg, name))
    for attr in attrs:
        if attr not in ALL_ARGS:
            raise TypeError('Invalid attr %r found in %s arg' % (arg, name))
