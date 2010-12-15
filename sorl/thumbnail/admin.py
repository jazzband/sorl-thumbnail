from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail.fields import ImageField
from sorl.thumbnail import default


class AdminImageWidget(forms.FileInput):
    """
    An ImageField Widget for django.contrib.admin that shows a thumbnailed
    image as well as a link to the current one if it hase one.
    """
    thumbnail_geometry = '150x150'

    def __init__(self, attrs=None, thumbnail_geometry=None):
        if thumbnail_geometry:
            self.thumbnail_geometry = thumbnail_geometry
        super(AdminImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = super(AdminImageWidget, self).render(name, value, attrs)
        if value and hasattr(value, 'url'):
            try:
                mini = default.backend.get_thumbnail(value, self.thumbnail_geometry)
            except Exception:
                pass
            else:
                output = (
                    u'<div style="float:left">'
                    u'<a style="width:%spx;display:block;margin:0 0 10px" class="thumbnail" target="_blank" href="%s">'
                    u'<img src="%s"></a>%s</div>'
                    ) % (mini.width, value.url, mini.url, output)
        return mark_safe(output)


class AdminClearWidget(forms.CheckboxInput):
    def render(self, name, value, attrs=None):
        output = super(AdminClearWidget, self).render(name, value, attrs)
        return (
            u'<div style="clear:both;padding-top:5px">'
            u'<label for="id_%s">%s:</label>%s'
            u'</div>'
            ) % (name, _('Clear image'), output)


class AdminClearableImageWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (AdminImageWidget(attrs=attrs), AdminClearWidget())
        super(AdminClearableImageWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return (value, False)
        return (None, None)


class AdminImageMixin(object):
    """
    This is for lazy people to mix-in in their ModelAdmin class.
    """
    formfield_overrides = {
        ImageField: {
            'widget': AdminClearableImageWidget,
        }
    }

