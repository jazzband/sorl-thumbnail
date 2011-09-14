from django.conf import settings as user_settings
from django.utils.functional import LazyObject
from sorl.thumbnail.conf import defaults


class Settings(object):
    pass


class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings()
        self._update(defaults)
        self._update(user_settings)

    def _update(self, obj):
        for attr in dir(obj):
            if attr == attr.upper():
                setattr(self, attr, getattr(obj, attr))


settings = LazySettings()
