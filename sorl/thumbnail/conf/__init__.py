from sorl.thumbnail.conf import defaults
from django.conf import settings as _settings
from django.conf import UserSettingsHolder


sorl_settings = UserSettingsHolder(_settings)
for setting in dir(defaults):
    if setting == setting.upper() and not hasattr(sorl_settings, setting):
        setattr(sorl_settings, setting, getattr(defaults, setting))
settings = sorl_settings
