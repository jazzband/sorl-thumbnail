from os.path import join as pjoin, abspath, dirname, pardir


PROJ_ROOT = abspath(pjoin(dirname(__file__), pardir))
THUMBNAIL_PREFIX = 'test/cache/'
THUMBNAIL_DEBUG = True
THUMBNAIL_LOG_HANDLER = {
    'class': 'sorl.thumbnail.log.ThumbnailLogHandler',
    'level': 'ERROR',
}
ADMINS = (
    ('Sorl', 'thumbnail@sorl.net'),
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'thumbnail_tests',
    }
}
MEDIA_ROOT = pjoin(PROJ_ROOT, 'media')
MEDIA_URL = '/media/'
ROOT_URLCONF = 'tests.urls'
INSTALLED_APPS = (
    'thumbnail',
    'thumbnail_tests',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
)

