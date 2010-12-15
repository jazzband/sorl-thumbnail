from django import forms
from sorl.thumbnail import get_thumbnail


class ImageWidgetBase(forms.FileInput):
    thumbnail_geometry = '150x150'


class AdminImageWidget(ImageWidgetBase):
    """
    An ImageField Widget for django.contrib.admin that shows a thumbnailed
    image as well as a link to the current one if it hase one.
    """
    def render(self, name, value, attrs=None):
        output = super(AdminImageWidget, self).render(name, value, attrs)
        if value and hasattr(value, 'url'):
            try:
                mini = get_thumbnail(value, self.thumbnail_geometry)
            except Exception:
                pass
            else:
                output = (
                    '<div style="float:left">'
                    '<a style="display:block;margin:0 0 10px" class="thumbnail" target="_blank" href="%s">'
                    '<img src="%s"></a>%s</div>' % (value.url, mini.url, output)
                    )
        return mark_safe(output)

