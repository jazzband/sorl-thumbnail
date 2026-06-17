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
THUMBNAIL_KVSTORE = 'tests.thumbnail_tests.kvstore.TestKVStore'
THUMBNAIL_STORAGE = 'default'
STORAGES = {
    "default": {
        "BACKEND": "tests.thumbnail_tests.storage.TestStorage",
    },
}

ADMINS = (
    ('Sorl', 'thumbnail@sorl.net'),
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
MEDIA_ROOT = pjoin(PROJ_ROOT, 'media')
MEDIA_URL = '/media/'
ROOT_URLCONF = 'tests.thumbnail_tests.urls'
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'sorl.thumbnail',
    'tests.thumbnail_tests',
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
SILENCED_SYSTEM_CHECKS = [
    # The admin is in INSTALLED_APPS for template discovery only, so silence
    # checks about auth and messages not installed.
    "admin.E402",
    "admin.E404",
    "admin.E406",
    "admin.W411",
]
THUMBNAIL_REDIS_SSL = False
