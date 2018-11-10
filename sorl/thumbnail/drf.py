from rest_framework import serializers
from sorl.thumbnail.default import backend

THUMBNAIL_OPTIONS = set(backend.default_options) | set(k for k, v in backend.extra_options)


class ImageField(serializers.ImageField):
    def __init__(self, resize=None, *args, **kwargs):
        self.resize = resize
        if self.resize:
            self.thumbnail_options = {
                key: kwargs.pop(key)
                for key in THUMBNAIL_OPTIONS if key in kwargs
            }
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if self.resize and value:
            return backend.get_thumbnail(value, self.resize, **self.thumbnail_options).url
        return super(ImageField, self).to_representation(value)
