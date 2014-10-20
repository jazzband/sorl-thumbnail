from os.path import join as pjoin, abspath, dirname, pardir

import django

SECRET_KEY = 'SECRET'
PROJ_ROOT = abspath(pjoin(dirname(__file__), pardir))
DATA_ROOT = pjoin(PROJ_ROOT, 'data')
THUMBNAIL_PREFIX = 'test/cache/'
THUMBNAIL_DEBUG = True
THUMBNAIL_LOG_HANDLER = {
    'class': 'sorl.thumbnail.log.ThumbnailLogHandler',
    'level': 'ERROR',
}
THUMBNAIL_KVSTORE = 'thumbnail_tests.kvstore.TestKVStore'
THUMBNAIL_STORAGE = 'thumbnail_tests.storage.TestStorage'
DEFAULT_FILE_STORAGE = 'thumbnail_tests.storage.TestStorage'
ADMINS = (
    ('Sorl', 'thumbnail@sorl.net'),
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
MEDIA_ROOT = pjoin(PROJ_ROOT, 'media')
MEDIA_URL = '/media/'
ROOT_URLCONF = 'thumbnail_tests.urls'
if django.VERSION < (1, 6):
    INSTALLED_APPS = (
        'thumbnail',
        'thumbnail_tests',
    )
else:
    INSTALLED_APPS = (
        'sorl.thumbnail',
        'tests.thumbnail_tests',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
