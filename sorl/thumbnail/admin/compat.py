from __future__ import unicode_literals
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail.fields import ImageField, ImageFormField
from sorl.thumbnail.shortcuts import get_thumbnail


class ClearableImageFormField(forms.MultiValueField):
    def __init__(self, max_length=None, **kwargs):
        fields = (
            ImageFormField(max_length=max_length, **kwargs),
            forms.BooleanField()
        )
        super(ClearableImageFormField, self).__init__(fields, **kwargs)

    def compress(self, data_list):
        if data_list:
            if not data_list[0] and data_list[1]:
                return False
            return data_list[0]


class AdminImageWidget(forms.FileInput):
    """
    An ImageField Widget for django.contrib.admin that shows a thumbnailed
    image as well as a link to the current one if it hase one.
    """

    def render(self, name, value, attrs=None):
        output = super(AdminImageWidget, self).render(name, value, attrs)
        if value and hasattr(value, 'url'):
            ext = 'JPG'
            try:
                aux_ext = str(value).split('.')
                if aux_ext[len(aux_ext)-1].lower() == 'png':
                    ext = 'PNG'
            except: 
                pass
            try:
                mini = get_thumbnail(value, 'x80', upscale=False, format=ext)
            except Exception:
                pass
            else:
                output = (
                             '<div style="float:left">'
                             '<a style="width:%spx;display:block;margin:0 0 10px" class="thumbnail" target="_blank" href="%s">'
                             '<img src="%s"></a>%s</div>'
                         ) % (mini.width, value.url, mini.url, output)
        return mark_safe(output)


class AdminClearWidget(forms.CheckboxInput):
    def render(self, name, value, attrs=None):
        output = super(AdminClearWidget, self).render(name, value, attrs)
        output = (
                     '<div style="clear:both;padding-top:5px">'
                     '<label for="id_%s">%s:</label>%s'
                     '</div>'
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
    This is a mix-in for ModelAdmin subclasses to make ``ImageField`` show nicer
    form class and widget
    """

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, ImageField):
            if not db_field.blank:
                return db_field.formfield(widget=AdminImageWidget)
            return db_field.formfield(
                form_class=ClearableImageFormField,
                widget=AdminClearableImageWidget,
            )
        sup = super(AdminImageMixin, self)
        return sup.formfield_for_dbfield(db_field, **kwargs)

