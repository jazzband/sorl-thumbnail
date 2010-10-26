import Image
import os
import unittest
from django.conf import settings
from os.path import join as pjoin
from test_app.models import Item
from sorl.thumbnail.helpers import get_thumbnail


class ThumbnailTestCase(unittest.TestCase):
    def setUp(self):
        dims = [
            (500, 500),
        ]
        self.test_images = []
        for dim in dims:
            fn = pjoin(settings.MEDIA_ROOT, '%sx%s.jpg' % dim)
            im = Image.new('L', dim)
            im.save(fn)
            self.test_images.append(fn)

    def tearDown(self):
        for fn in self.test_images:
            os.remove(fn)

    def testItem(self):
        item = Item.objects.get(image='500x500.jpg')
        t = get_thumbnail(item.image, '400x300')

