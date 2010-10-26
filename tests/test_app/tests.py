import Image
import os
import unittest
import shutil
from django.conf import settings
from os.path import join as pjoin
from test_app.models import Item
from sorl.thumbnail.helpers import get_thumbnail


class ThumbnailTestCase(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        dims = [
            (500, 500),
        ]
        for dim in dims:
            fn = pjoin(settings.MEDIA_ROOT, '%sx%s.jpg' % dim)
            im = Image.new('L', dim)
            im.save(fn)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def testBasicGeometry(self):
        item = Item.objects.get(image='500x500.jpg')
        t = get_thumbnail(item.image, '400x300', crop='1000%')
        self.assertEqual(t.x, 300)
        self.assertEqual(t.y, 300)

