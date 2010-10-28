import socket
import sys
from django.conf import settings


# When True ThumbnailNode.render can raise errors
THUMBNAIL_DEBUG = False

# Thumbnail backend
THUMBNAIL_BACKEND = 'sorl.thumbnail.backends.db.Thumbnail'

# Thumbnail engine
THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.engine_pgmagick.ThumbnailEngine'

# Default storage for the generated thumbnail
THUMBNAIL_STORAGE = settings.DEFAULT_FILE_STORAGE

# Thumbnail filename prefix
THUMBNAIL_PREFIX = 'cache/'

# Image format, common formats are: JPEG, PNG
# Make sure the backend can handle the format you specify
THUMBNAIL_FORMAT = 'JPEG'

# Colorspace, backends are required to implement: RGB, GRAY
# Setting this to None will keep the original colorspace.
THUMBNAIL_COLORSPACE = 'RGB'

# Should we upscale images
THUMBNAIL_UPSCALE = True

# Quality, 0-100
THUMBNAIL_QUALITY = 95

# DB Cache timeout. You should keep this at maximum since invalidating is taken
# care of already
THUMBNAIL_CACHE_TIMEOUT = sys.maxint

# Cache prefix, this is up to the engine or backend to use.
THUMBNAIL_CACHE_PREFIX = 'sorl-thumbnail-'

# Return this when an error is raised and THUMBNAIL_DEBUG is False
THUMBNAIL_ERROR = ''

# Timeout for fetching remote images
THUMBNAIL_URL_TIMEOUT = socket._GLOBAL_DEFAULT_TIMEOUT

# This means sorl-thumbnail will generate and serve a generated dummy image
# regardless of the thumbnail source content
THUMBNAIL_DUMMY = False

# The probability of returning an empty image when THUMBNAIL_MOCKUP is set to
# True
THUMBNAIL_DUMMY_EMPTY_P = 0

# Sets the source image ratio for dummy generation
THUMBNAIL_DUMMY_RATIO = 3 / 2

