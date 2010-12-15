from django.contrib import admin
from django.db import models
from sorl.thumbnail.fields import ImageField
from sorl.thumbnail.widgets import AdminImageWidget


class AdminThumbnailMixin(object):
    """
    This is for lazy people to mix-in in their ModelAdmin class.
    """
    formfield_overrides = {
        ImageField: {
            'widget': AdminImageWidget,
        }
    }


class ModelAdmin(AdminThumbnailMixin, admin.ModelAdmin):
    """
    This is for wicked stupid lazy people to inherit from.
    """
    pass

