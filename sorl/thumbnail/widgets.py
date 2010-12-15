from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail import default


class ClearableFileWidget(forms.MultiWidget):
    def __init__(self, widgets, attrs=None):
        widgets = (forms.FileInput(), ClearImageWidget)
        super(ClearableFileWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        return [value, False]


class AdminImageWidget(ClearableFileWidget):
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
            mini = default.backend.get_thumbnail(value, self.thumbnail_geometry)
            output = (
                '<div style="float:left">'
                '<a style="display:block;margin:0 0 10px" class="thumbnail" target="_blank" href="%s">'
                '<img src="%s"></a>%s</div>' % (value.url, mini.url, output)
                )
        return mark_safe(output)


class ClearImageWidget(forms.CheckboxInput):
    def render(self, name, value, attrs=None):
        output = super(ClearImageWidget, self).render(name, value, attrs)
        return output

