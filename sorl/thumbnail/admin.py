from django.contrib import admin
from django.db import models
from sorl.thumbnail.widgets import AdminImageWidget


class AdminThumbnailMixin(object):
    """
    This is for lazy people to mix-in in their ModelAdmin class. We use
    ``django.db.models.ImageField`` since we are so lazy that we also want
    thumbnails for all ImageFields.
    """
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget}
    }


class ModelAdmin(AdminThumbnailMixin, admin.ModelAdmin):
    """
    This is for wicked stupid lazy people to inherit from.
    """
    pass

