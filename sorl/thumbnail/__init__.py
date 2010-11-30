from sorl.thumbnail.fields import ImageField


#
# configure logging
#
import logging
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class


handler = get_module_class(settings.THUMBNAIL_LOG_HANDLER['class'])()
level = settings.THUMBNAIL_LOG_HANDLER.get('level')
if level:
    level = getattr(logging, level)
    handler.setLevel(level)
logging.getLogger('sorl.thumbnail').addHandler(handler)

