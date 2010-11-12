from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class
from sorl.thumbnail.images import ImageFile


__all__ = ('ImageField', 'ImageFormField')


class ImageField(models.FileField):
    def delete_file(self, instance, sender, **kwargs):
        """
        Adds deletion of thumbnails and key kalue store references to the
        parent class implementation.
        """
        file_ = getattr(instance, self.attname)
        # If no other object of this type references the file,
        # and it's not the default value for future objects,
        # delete it from the backend.
        if file_ and file_.name != self.default and \
            not sender._default_manager.filter(**{self.name: file_.name}):
                file_.delete(save=False)
                # now delete the kvstore references and thumbnails
                image_file = ImageFile(file_)
                kvstore = get_module_class(settings.THUMBNAIL_KVSTORE)()
                kvstore.delete(image_file)
        elif file_:
            # Otherwise, just close the file, so it doesn't tie up resources.
            file_.close()

    def formfield(self, **kwargs):
        defaults = {'form_class': ImageFormField}
        defaults.update(kwargs)
        return super(ImageField, self).formfield(**defaults)


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
        engine = get_module_class(settings.THUMBNAIL_ENGINE)()
        if not engine.is_valid_image(raw_data):
            raise forms.ValidationError(self.error_messages['invalid_image'])
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f

