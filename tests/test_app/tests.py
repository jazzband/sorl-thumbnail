import Image
import os
import unittest
import shutil
from django.conf import settings
from django.template.loader import render_to_string
from os.path import join as pjoin
from test_app.models import Item
from sorl.thumbnail.helpers import get_thumbnail, get_module_class, ThumbnailError
from sorl.thumbnail.parsers import parse_crop, parse_geometry


class ParsersTestCase(unittest.TestCase):
    def testAliasCrop(self):
        crop = parse_crop('center', (500, 500), (400, 400))
        self.assertEqual(crop, (50, 50, 450, 450))
        crop = parse_crop('right', (500, 500), (400, 400))
        self.assertEqual(crop, (100, 50, 500, 450))

    def testPercentCrop(self):
        crop = parse_crop('50% 0%', (500, 500), (400, 400))
        self.assertEqual(crop, (50, 0, 450, 400))
        crop = parse_crop('10% 80%', (500, 500), (400, 400))
        self.assertEqual(crop, (10, 80, 410, 480))

    def testPxCrop(self):
        crop = parse_crop('200px 33px', (500, 500), (400, 400))
        self.assertEqual(crop, (100, 33, 500, 433))

    def testBadCrop(self):
        self.assertRaises(ThumbnailError, parse_crop, '-200px', (500, 500), (400, 400))

    def testGeometry(self):
        g = parse_geometry('222x30')
        self.assertEqual(g, (222, 30))
        g = parse_geometry('222')
        self.assertEqual(g, (222, None))
        g = parse_geometry('x999')
        self.assertEqual(g, (None, 999))


class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        dims = [
            (500, 500),
            (100, 100),
        ]
        for dim in dims:
            name = '%sx%s.jpg' % dim
            fn = pjoin(settings.MEDIA_ROOT, name)
            im = Image.new('L', dim)
            im.save(fn)
            Item.objects.get_or_create(image=name)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def testSimple(self):
        item = Item.objects.get(image='500x500.jpg')
        t = get_thumbnail(item.image, '400x300', crop='center')
        self.assertEqual(t.x, 400)
        self.assertEqual(t.y, 300)
        t = get_thumbnail(item.image, '1200x900', crop='13% 89%')
        self.assertEqual(t.x, 1200)
        self.assertEqual(t.y, 900)

    def testUpscale(self):
        item = Item.objects.get(image='100x100.jpg')
        t = get_thumbnail(item.image, '400x300', upscale=False)
        self.assertEqual(t.x, 100)
        self.assertEqual(t.y, 100)
        t = get_thumbnail(item.image, '400x300', upscale=True)
        self.assertEqual(t.x, 300)
        self.assertEqual(t.y, 300)

    def testMargin(self):
        item = Item.objects.get(image='100x100.jpg')
        t = get_thumbnail(item.image, '200x800')
        self.assertEqual(t.margin, '300px 0px 300px 0px')
        t = get_thumbnail(item.image, '200x800', upscale=False)
        self.assertEqual(t.margin, '350px 50px 350px 50px')
        t = get_thumbnail(item.image, '200x800', crop='noop')
        self.assertEqual(t.margin, '0px -300px 0px -300px')
        t = get_thumbnail(item.image, '200')
        self.assertEqual(t.margin, '0px 0px 0px 0px')
        t = get_thumbnail(item.image, 'x999')
        self.assertEqual(t.margin, '0px 0px 0px 0px')


class TemplateTestCaseA(SimpleTestCase):
    def testModel(self):
        item = Item.objects.get(image='500x500.jpg')
        val = render_to_string('thumbnail1.html', {
            'item': item,
        }).strip()
        self.assertEqual(val, u'<img style="margin:0px 0px 0px 0px" width="200" height="100">')
        val = render_to_string('thumbnail2.html', {
            'item': item,
        }).strip()
        self.assertEqual(val, u'<img style="margin:0px 50px 0px 50px" width="100" height="100">')


class TemplateTestCaseB(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def testUrl(self):
        val = render_to_string('thumbnail3.html', {}).strip()
        self.assertEqual(val, '<img style="margin:0px 0px 0px 0px" width="20" height="20">')

    def testPortrait(self):
        val = render_to_string('thumbnail4.html', {
            'source': 'http://www.aino.se/media/i/logo.png',
            'dims': 'x666',
        }).strip()
        self.assertEqual(val, '<img src="/media/test/cache/51/db/51dbfb4a3f6177917cd86dae19cc4952.jpg" width="1984" height="666" class="landscape">')

