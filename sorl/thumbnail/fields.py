from __future__ import with_statement
from django.db import models
from django.db.models import Q
from django import forms
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail.conf import settings
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail import default
from sorl.thumbnail.widgets import AdminImageWidget


__all__ = ('ImageField', 'ImageFormField')


class South(object):
    """
    Just a south introspection Mixin
    """
    def south_field_triple(self):
        from south.modelsinspector import introspector
        cls_name = '%s.%s' % (self.__class__.__module__ , self.__class__.__name__)
        args, kwargs = introspector(self)
        return (cls_name, args, kwargs)

#
# Model fields
#
class ImageField(South, models.FileField):
    def delete_file(self, instance, sender, **kwargs):
        """
        Adds deletion of thumbnails and key kalue store references to the
        parent class implementation.
        """
        file_ = getattr(instance, self.attname)
        # If no other object of this type references the file, and it's not the
        # default value for future objects, delete it from the backend.
        query = Q(**{self.name: file_.name}) & ~Q(pk=instance.pk)
        qs = sender._default_manager.filter(query)
        if (file_ and file_.name != self.default and not qs):
            default.backend.delete(file_)
        elif file_:
            # Otherwise, just close the file, so it doesn't tie up resources.
            file_.close()

    def formfield(self, **kwargs):
        defaults = {'form_class': ClearableImageFormField}
        defaults.update(kwargs)
        return super(ImageField, self).formfield(**defaults)

    def save_form_data(self, instance, data):
        if data is not None:
            # We could try to delete the file here since its deleted or
            # replaced. This is not done in Django 1.3. ``delete_file`` is
            # currently only called on instance post_delete signal.
            #self.delete_file(instance, instance.__class__)
            setattr(instance, self.name, data or '')

#
# Form fields
#
class ImageFormField(forms.FileField):
    default_error_messages = {
        'invalid_image': _(u"Upload a valid image. The file you uploaded was "
                           u"either not an image or a corrupted image."),
    }

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid image (GIF,
        JPG, PNG, possibly others -- whatever the engine supports).
        """
        f = super(ImageFormField, self).to_python(data)
        if f is None:
            return None
        # We need to get a file raw data to validate it.
        if hasattr(data, 'temporary_file_path'):
            with open(data.temporary_file_path(), 'rb') as fp:
                raw_data = fp.read()
        elif hasattr(data, 'read'):
            raw_data = data.read()
        else:
            raw_data = data['content']
        if not default.engine.is_valid_image(raw_data):
            raise forms.ValidationError(self.error_messages['invalid_image'])
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f


class ClearableImageFormField(forms.MultiValueField):
    def __init__(self, max_length=None, *args, **kwargs):
        super(forms.MultiValueField, self).__init__(*args, **kwargs)
        self.fields = (
            ImageFormField(max_length=max_length, *args, **kwargs),
            forms.BooleanField(required=False)
            )

    def compress(self, data_list):
        if data_list:
            if not data_list[0] and data_list[1]:
                return False
            return data_list[0]

