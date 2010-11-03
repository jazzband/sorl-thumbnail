import Image
import os
import unittest
import shutil
import operator
import random
from django.conf import settings
from django.template.loader import render_to_string
from os.path import join as pjoin
from test_app.models import Item
from sorl.thumbnail.helpers import get_module_class, ThumbnailError
from sorl.thumbnail.parsers import parse_crop, parse_geometry
from sorl.thumbnail.backends.base import suffix_key
from sorl.thumbnail.engines.PIL import ThumbnailEngine as EnginePil
from sorl.thumbnail.engines.pgmagick import ThumbnailEngine as EnginePgmagick
from sorl.thumbnail.storage import ImageFile
from sorl.thumbnail.templatetags.thumbnail import margin


class ParsersTestCase(unittest.TestCase):
    def testAliasCrop(self):
        crop = parse_crop('center', (500, 500), (400, 400))
        self.assertEqual(crop, (50, 50))
        crop = parse_crop('right', (500, 500), (400, 400))
        self.assertEqual(crop, (100, 50))

    def testPercentCrop(self):
        crop = parse_crop('50% 0%', (500, 500), (400, 400))
        self.assertEqual(crop, (50, 0))
        crop = parse_crop('10% 80%', (500, 500), (400, 400))
        self.assertEqual(crop, (10, 80))

    def testPxCrop(self):
        crop = parse_crop('200px 33px', (500, 500), (400, 400))
        self.assertEqual(crop, (100, 33))

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
        self.backend = get_module_class(settings.THUMBNAIL_BACKEND)()
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
        t = self.backend.get_thumbnail(item.image, '400x300', crop='center')
        self.assertEqual(t.x, 400)
        self.assertEqual(t.y, 300)
        t = self.backend.get_thumbnail(item.image, '1200x900', crop='13% 89%')
        self.assertEqual(t.x, 1200)
        self.assertEqual(t.y, 900)

    def testUpscale(self):
        item = Item.objects.get(image='100x100.jpg')
        t = self.backend.get_thumbnail(item.image, '400x300', upscale=False)
        self.assertEqual(t.x, 100)
        self.assertEqual(t.y, 100)
        t = self.backend.get_thumbnail(item.image, '400x300', upscale=True)
        self.assertEqual(t.x, 300)
        self.assertEqual(t.y, 300)

    def testStoreThumbnails(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.backend.store_delete_thumbnails(im)
        th1 = self.backend.get_thumbnail(im, '50')
        th2 = self.backend.get_thumbnail(im, 'x50')
        th3 = self.backend.get_thumbnail(im, '20x20')
        self.assertEqual(
            set([th1.name, th2.name, th3.name]),
            set(self.backend._store_get(suffix_key(im.key)))
            )
        self.backend.store_delete_thumbnails(im)
        self.assertEqual(
            None,
            self.backend._store_get(suffix_key(im.key))
            )

    def testIsPortrait(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        th = self.backend.get_thumbnail(im, '50x200', crop='center')
        self.assertEqual(th.is_portrait(), True)
        th = self.backend.get_thumbnail(im, '500x2', crop='center')
        self.assertEqual(th.is_portrait(), False)

    def testMargin(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.assertEqual(margin(im, '1000x1000'), '250px 250px 250px 250px')
        self.assertEqual(margin(im, '800x1000'), '250px 150px 250px 150px')
        self.assertEqual(margin(im, '500x500'), '0px 0px 0px 0px')
        self.assertEqual(margin(im, '500x501'), '0px 0px 1px 0px')
        self.assertEqual(margin(im, '503x500'), '0px 2px 0px 1px')
        self.assertEqual(margin(im, '300x300'), '-100px -100px -100px -100px')

    def testStoreGetSet(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.backend.store_delete(im)
        self.assertEqual(self.backend.store_get(im), False)
        self.backend.store_set(im)
        self.assertEqual(im.size, (500, 500))

    def testStoreEmptyAll(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.backend._store_empty_all()
        self.assertEqual(self.backend.store_get(im), False)


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
        try:
            shutil.rmtree(settings.MEDIA_ROOT)
        except Exception:
            pass

    def testUrl(self):
        val = render_to_string('thumbnail3.html', {}).strip()
        self.assertEqual(val, '<img style="margin:0px 0px 0px 0px" width="20" height="20">')

    def testPortrait(self):
        val = render_to_string('thumbnail4.html', {
            'source': 'http://www.aino.se/media/i/logo.png',
            'dims': 'x666',
        }).strip()
        self.assertEqual(val, '<img src="/media/test/cache/75/1a/751a864d2c7b8327f8ce28ecfbd63618.jpg" width="1984" height="666" class="landscape">')

    def testEmpty(self):
        val = render_to_string('thumbnail5.html', {}).strip()
        self.assertEqual(val, '<p>empty</p>')


class CropTestCase(unittest.TestCase):
    def setUp(self):
        self.backend = get_module_class(settings.THUMBNAIL_BACKEND)()
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        # portrait
        name = 'portrait.jpg'
        fn = pjoin(settings.MEDIA_ROOT, name)
        im = Image.new('L', (100, 200))
        im.paste(255, (0, 0, 100, 100))
        im.save(fn)
        self.portrait = ImageFile(Item.objects.get_or_create(image=name)[0].image)
        self.backend.store_delete(self.portrait)

        # landscape
        name = 'landscape.jpg'
        fn = pjoin(settings.MEDIA_ROOT, name)
        im = Image.new('L', (200, 100))
        im.paste(255, (0, 0, 100, 100))
        im.save(fn)
        self.landscape = ImageFile(Item.objects.get_or_create(image=name)[0].image)
        self.backend.store_delete(self.landscape)

    def testPortraitCrop(self):
        def mean_pixel(x, y):
            values = im.getpixel((x, y))
            if not isinstance(values, (tuple, list)):
                values = [values]
            return reduce(operator.add, values) / len(values)
        for crop in ('center', '88% 50%', '50px'):
            th = self.backend.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = EnginePil()
            im = engine.get_image(th)
            self.assertEqual(mean_pixel(50,0), 255)
            self.assertEqual(mean_pixel(50,45), 255)
            self.assertEqual(250 < mean_pixel(50,49) <= 255, True)
            self.assertEqual(mean_pixel(50,55), 0)
            self.assertEqual(mean_pixel(50,99), 0)
        for crop in ('top', '0%', '0px'):
            th = self.backend.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = EnginePil()
            im = engine.get_image(th)
            for x in xrange(0, 99, 10):
                for y in xrange(0, 99, 10):
                    self.assertEqual(250 < mean_pixel(x, y) <= 255, True)
        for crop in ('bottom', '100%', '100px'):
            th = self.backend.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = EnginePil()
            im = engine.get_image(th)
            for x in xrange(0, 99, 10):
                for y in xrange(0, 99, 10):
                    self.assertEqual(0 <= mean_pixel(x, y) < 5, True)

    def testLandscapeCrop(self):
        def mean_pixel(x, y):
            values = im.getpixel((x, y))
            if not isinstance(values, (tuple, list)):
                values = [values]
            return reduce(operator.add, values) / len(values)
        for crop in ('center', '50% 200%', '50px 700px'):
            th = self.backend.get_thumbnail(self.landscape, '100x100', crop=crop)
            engine = EnginePil()
            im = engine.get_image(th)
            self.assertEqual(mean_pixel(0, 50), 255)
            self.assertEqual(mean_pixel(45, 50), 255)
            self.assertEqual(250 < mean_pixel(49, 50) <= 255, True)
            self.assertEqual(mean_pixel(55, 50), 0)
            self.assertEqual(mean_pixel(99, 50), 0)
        for crop in ('left', '0%', '0px'):
            th = self.backend.get_thumbnail(self.landscape, '100x100', crop=crop)
            engine = EnginePil()
            im = engine.get_image(th)
            for x in xrange(0, 99, 10):
                for y in xrange(0, 99, 10):
                    self.assertEqual(250 < mean_pixel(x, y) <= 255, True)
        for crop in ('right', '100%', '100px'):
            th = self.backend.get_thumbnail(self.landscape, '100x100', crop=crop)
            engine = EnginePil()
            im = engine.get_image(th)
            for x in xrange(0, 99, 10):
                for y in xrange(0, 99, 10):
                    self.assertEqual(0 <= mean_pixel(x, y) < 5, True)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)


