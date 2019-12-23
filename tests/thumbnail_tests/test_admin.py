from django.test import SimpleTestCase

from sorl.thumbnail.admin.current import AdminImageWidget


class AdminImageWidgetTests(SimpleTestCase):
    def test_render_renderer_argument(self):
        w = AdminImageWidget()
        self.assertHTMLEqual(w.render('name', 'value', renderer=None), '<input type="file" name="name">')
