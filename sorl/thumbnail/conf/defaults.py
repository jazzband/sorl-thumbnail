import sys
from django.conf import settings


# When True ThumbnailNode.render can raise errors
THUMBNAIL_DEBUG = False

# Backend
THUMBNAIL_BACKEND = 'sorl.thumbnail.base.ThumbnailBackend'

# Key-value store, ships with:
# sorl.thumbnail.kvstores.redis_kvstore.KVStore
# sorl.thumbnail.kvstores.cached_db_kvstore.KVStore
# Redis is preferred but requires some more work, see docs
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'

# Engine, ships with:
# sorl.thumbnail.engines.pgmagick_engine.Engine
# sorl.thumbnail.engines.pil_engine.Engine
# pgmagick is preferred but requires some more work, se docs
THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.pil_engine.Engine'

# Storage for the generated thumbnails
THUMBNAIL_STORAGE = settings.DEFAULT_FILE_STORAGE

# Redis settings
THUMBNAIL_REDIS_HOST = 'localhost'
THUMBNAIL_REDIS_PORT = 6379
THUMBNAIL_REDIS_DB = 0

# Cache timeout for ``cached_db`` store. You should probably keep this at
# maximum or ``None`` if your caching backend can handle that as infinate.
THUMBNAIL_CACHE_TIMEOUT = sys.maxint

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

# This means sorl.thumbnail will generate and serve a generated dummy image
# regardless of the thumbnail source content
THUMBNAIL_DUMMY = False

# Sets the source image ratio for dummy generation of images with only width
# or height given
THUMBNAIL_DUMMY_RATIO = 3.0 / 2

