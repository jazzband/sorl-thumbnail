import os.path

from django.db.models.fields import ImageField
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
    def __init__(self, thumbnail, extra_thumbnails=None, **kwargs):
        super(ImageWithThumbnailsField, self).__init__(**kwargs)
        _verify_thumbnail_attrs(thumbnail)
        if extra_thumbnails:
            for extra, attrs in extra_thumbnails.items():
                name = "%r of 'extra_thumbnails'"
                _verify_thumbnail_attrs(attrs, name)
        self.thumbnail = thumbnail
        self.extra_thumbnails = extra_thumbnails

    def get_internal_type(self):
        return "ImageField"

    def get_manipulator_field_objs(self):
        return [oldforms.ImageUploadField, oldforms.HiddenField]

    def contribute_to_class(self, cls, name):
        super(ImageWithThumbnailsField, self).contribute_to_class(cls, name)
        self._contribute_thumbnail(cls, name, self.thumbnail)
        if self.extra_thumbnails:
            for extra, thumbnail in self.extra_thumbnails.items():
                if not extra:
                    continue
                n = '%s_%s' % (name, extra)
                self._contribute_thumbnail(cls, n, thumbnail)

    def _contribute_thumbnail(self, cls, name, thumbnail):
        func = curry(_get_thumbnail, field=self, attrs=thumbnail)
        tag_func = curry(_get_thumbnail_tag, field=self, attrs=thumbnail)
        # Make it safe for contrib.admin
        tag_func.allow_tags = True
        setattr(cls, 'get_%s_thumbnail' % name, func)
        setattr(cls, 'get_%s_thumbnail_tag' % name, tag_func)

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

def _get_thumbnail(model_instance, field, attrs):
    # Build kwargs
    kwargs = {}
    for k, v in attrs.items():
        kwargs[ALL_ARGS[k]] = v
    # Build relative source path
    filename = getattr(model_instance, 'get_%s_filename' % field.name)()
    media_root_len = len(os.path.normpath(settings.MEDIA_ROOT))
    filename = os.path.normpath(filename)
    filename = filename[media_root_len:].lstrip(os.path.sep)
    # Return thumbnail
    return DjangoThumbnail(filename, **kwargs)

def _get_thumbnail_tag(model_instance, field, attrs):
    thumb = _get_thumbnail(model_instance, field, attrs)
    tag = '<img src="%s" width="%s" height="%s" alt="" />' % (
        escape(thumb), thumb.width(), thumb.height())
    return mark_safe(tag)
