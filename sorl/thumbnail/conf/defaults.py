from django.conf import settings


# When True ThumbnailNode.render can raise errors
THUMBNAIL_DEBUG = False

# Backend
THUMBNAIL_BACKEND = 'sorl.thumbnail.base.ThumbnailBackend'

# Key-value store, ships with:
# sorl.thumbnail.kvstores.cached_db_kvstore.KVStore
# sorl.thumbnail.kvstores.redis_kvstore.KVStore
# Redis requires some more work, see docs
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'

# Change this to something else for MSSQL
THUMBNAIL_KEY_DBCOLUMN = 'key'

# Engine, ships with:
# sorl.thumbnail.engines.convert_engine.Engine
# sorl.thumbnail.engines.pil_engine.Engine
# sorl.thumbnail.engines.pgmagick_engine.Engine
# convert is preferred but requires imagemagick or graphicsmagick, se docs
THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.pil_engine.Engine'

# Path to Imagemagick or Graphicsmagick ``convert`` and ``identify``.
THUMBNAIL_CONVERT = 'convert'
THUMBNAIL_IDENTIFY = 'identify'

# Storage for the generated thumbnails
THUMBNAIL_STORAGE = settings.DEFAULT_FILE_STORAGE

# Redis settings
THUMBNAIL_REDIS_DB = 0
THUMBNAIL_REDIS_PASSWORD = ''
THUMBNAIL_REDIS_HOST = 'localhost'
THUMBNAIL_REDIS_PORT = 6379
THUMBNAIL_REDIS_UNIX_SOCKET_PATH = None

# Cache timeout for ``cached_db`` store. You should probably keep this at
# maximum or ``0`` if your caching backend can handle that as infinate.
THUMBNAIL_CACHE_TIMEOUT = 3600 * 24 * 365 * 10 # 10 years

# Key prefix used by the key value store
THUMBNAIL_KEY_PREFIX = 'sorl-thumbnail'

# Thumbnail filename prefix
THUMBNAIL_PREFIX = 'cache/'

# Image format, common formats are: JPEG, PNG
# Make sure the backend can handle the format you specify
THUMBNAIL_FORMAT = 'JPEG'

# Colorspace, backends are required to implement: RGB, GRAY
# Setting this to None will keep the original colorspace.
THUMBNAIL_COLORSPACE = 'RGB'

# Should we upscale images by default
THUMBNAIL_UPSCALE = True

# Quality, 0-100
THUMBNAIL_QUALITY = 95

# Gaussian blur radius
THUMBNAIL_BLUR = 0

# Save as progressive when saving as jpeg
THUMBNAIL_PROGRESSIVE = True

# Orientate the thumbnail with respect to source EXIF orientation tag
THUMBNAIL_ORIENTATION = True

# This means sorl.thumbnail will generate and serve a generated dummy image
# regardless of the thumbnail source content
THUMBNAIL_DUMMY = False

# Thumbnail dummy (placeholder) source. Some you might try are:
# http://placekitten.com/%(width)s/%(height)s
# http://placekitten.com/g/%(width)s/%(height)s
# http://placehold.it/%(width)sx%(height)s
THUMBNAIL_DUMMY_SOURCE = 'http://dummyimage.com/%(width)sx%(height)s'

# Sets the source image ratio for dummy generation of images with only width
# or height given
THUMBNAIL_DUMMY_RATIO = 1.5

# Timeout, in seconds, to use when retrieving images with urllib2
THUMBNAIL_URL_TIMEOUT = None

