from django import forms
from django.test import SimpleTestCase
from django.forms.widgets import FileInput

from sorl.thumbnail.fields import ImageFormField


class ImageFormFieldTest(SimpleTestCase):

    def assertWidgetRendersTo(self, field, to):
        class Form(forms.Form):
            f = field
        self.assertHTMLEqual(str(Form()["f"]), to)

    def test_widget_attrs_default_accept(self):
        f = ImageFormField()
        self.assertEqual(f.widget_attrs(FileInput()), {'accept': 'image/*'})
        self.assertWidgetRendersTo(f, '<input type="file" name="f" accept="image/*" required id="id_f" />')
