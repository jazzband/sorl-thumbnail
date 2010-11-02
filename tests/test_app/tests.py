import Image
import os
import unittest
import shutil
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

    #def tearDown(self):
    #    shutil.rmtree(settings.MEDIA_ROOT)

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

    def testStoreGetSet(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.backend.store_delete(im)
        self.assertEqual(self.backend.store_get(im), False)
        self.backend.store_set(im)
        self.assertEqual(im.size, (500, 500))


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
    #def tearDown(self):
    #    try:
    #        shutil.rmtree(settings.MEDIA_ROOT)
    #    except Exception:
    #        pass

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
        name = 'palette.jpg'
        fn = pjoin(settings.MEDIA_ROOT, name)
        im = Image.new('RGB', (300, 300))
        im.paste((255, 255, 255), (100, 100, 199, 199))
        im.save(fn)
        self.palette = ImageFile(Item.objects.get_or_create(image=name)[0].image)

    def testCrop(self):
        th = self.backend.get_thumbnail(self.palette, '100x100', crop='top')
        print th.name
        #engine = EnginePil()
        #thim = engine.get_image(th)
        #print thim.getextrema()
        #print th.name

    def tearDown(self):
        pass
        #shutil.rmtree(settings.MEDIA_ROOT)

    def testOne(self):
        pass

