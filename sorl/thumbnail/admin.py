from sorl.thumbnail.fields import ImageField
from sorl.thumbnail.widgets import AdminClearableImageWidget


class AdminImageMixin(object):
    """
    This is for lazy people to mix-in in their ModelAdmin class.
    """
    formfield_overrides = {
        ImageField: {
            'widget': AdminClearableImageWidget,
        }
    }

