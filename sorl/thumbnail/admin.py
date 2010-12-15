from django.contrib import admin
from django.db import models
from sorl.thumbnail.fields import ImageField
from sorl.thumbnail.widgets import AdminClearableImageWidget, AdminImageWidget


class AdminImageMixin(object):
    """
    This is for lazy people to mix-in in their ModelAdmin class.
    """
    formfield_overrides = {
        ImageField: {
            'widget': AdminClearableImageWidget,
        }
    }


class ModelAdmin(AdminImageMixin, admin.ModelAdmin):
    """
    This is for wicked stupid lazy people to inherit from.
    """
    pass

