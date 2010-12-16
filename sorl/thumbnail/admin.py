from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail.fields import ImageField, ClearableImageFormField
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
        output = (
            u'<div style="clear:both;padding-top:5px">'
            u'<label for="id_%s">%s:</label>%s'
            u'</div>'
            ) % (name, _('Clear image'), output)
        return mark_safe(output)


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
    This is a mix-in for ModelAdmin subclasses to make ``ImageField`` show ncer
    form class and widget
    """
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, ImageField):
            return db_field.formfield(
                form_class=ClearableImageFormField,
                widget=AdminClearableImageWidget,
                )
        sup = super(AdminImageMixin, self)
        return sup.formfield_for_dbfield(db_field, **kwargs)

