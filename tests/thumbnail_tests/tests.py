#coding=utf-8
import logging
import operator
import os
import re
import shutil
from PIL import Image
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.test.client import Client
from django.utils import unittest
from os.path import join as pjoin
from sorl.thumbnail import default, get_thumbnail, delete
from sorl.thumbnail.conf import settings
from sorl.thumbnail.engines.pil_engine import Engine as PILEngine
from sorl.thumbnail.helpers import get_module_class, ThumbnailError
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.log import ThumbnailLogHandler
from sorl.thumbnail.parsers import parse_crop, parse_geometry
from sorl.thumbnail.templatetags.thumbnail import margin
from subprocess import Popen, PIPE
from thumbnail_tests.models import Item
from thumbnail_tests.storage import slog


handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)


class StorageTestCase(unittest.TestCase):
    def setUp(self):
        name = 'org.jpg'
        os.makedirs(settings.MEDIA_ROOT)
        fn = pjoin(settings.MEDIA_ROOT, name)
        Image.new('L', (100, 100)).save(fn)
        self.im = ImageFile(name)

    def test_a_new(self):
        slog.start_log()
        get_thumbnail(self.im, '50x50')
        log = slog.stop_log()
        actions = [
            # first see if the file exists
            'exists: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4.jpg',
            # open the original for thumbnailing
            'open: org.jpg',
            # save the file
            'save: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4.jpg',
            # check for filename
            'get_available_name: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4.jpg',
            # called by get_available_name
            'exists: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4.jpg',
            # save the 1.5 resolution version
            'save: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4@1.5x.jpg',
            'get_available_name: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4@1.5x.jpg',
            'exists: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4@1.5x.jpg',
            # save the 2 resolution version
            'save: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4@2x.jpg',
            'get_available_name: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4@2x.jpg',
            'exists: test/cache/cc/33/cc33e9e8b2355e7e2a9437319c046ad4@2x.jpg'
        ]
        self.assertEqual(log, actions)

    def test_b_cached(self):
        slog.start_log()
        get_thumbnail(self.im, '50x50')
        log = slog.stop_log()
        self.assertEqual(log, []) # now this should all be in cache

    def test_c_safe_methods(self):
        slog.start_log()
        im = default.kvstore.get(self.im)
        im.url, im.x, im.y
        log = slog.stop_log()
        self.assertEqual(log, [])

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)


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


class SimpleTestCaseBase(unittest.TestCase):
    def setUp(self):
        self.backend = get_module_class(settings.THUMBNAIL_BACKEND)()
        self.engine = get_module_class(settings.THUMBNAIL_ENGINE)()
        self.kvstore = get_module_class(settings.THUMBNAIL_KVSTORE)()
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        dims = [
            (500, 500),
            (100, 100),
            (200, 100),
        ]
        for dim in dims:
            name = '%sx%s.jpg' % dim
            fn = pjoin(settings.MEDIA_ROOT, name)
            im = Image.new('L', dim)
            im.save(fn)
            Item.objects.get_or_create(image=name)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)


class SimpleTestCase(SimpleTestCaseBase):
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

    def testUpscaleCrop(self):
        item = Item.objects.get(image='200x100.jpg')
        t = self.backend.get_thumbnail(item.image, '400x300', crop='center', upscale=False)
        self.assertEqual(t.x, 200)
        self.assertEqual(t.y, 100)
        t = self.backend.get_thumbnail(item.image, '400x300', crop='center', upscale=True)
        self.assertEqual(t.x, 400)
        self.assertEqual(t.y, 300)

    def testKVStore(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.kvstore.delete_thumbnails(im)
        th1 = self.backend.get_thumbnail(im, '50')
        th2 = self.backend.get_thumbnail(im, 'x50')
        th3 = self.backend.get_thumbnail(im, '20x20')
        self.assertEqual(
            set([th1.key, th2.key, th3.key]),
            set(self.kvstore._get(im.key, identity='thumbnails'))
            )
        self.kvstore.delete_thumbnails(im)
        self.assertEqual(
            None,
            self.kvstore._get(im.key, identity='thumbnails')
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

    def testKVStoreGetSet(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.kvstore.delete(im)
        self.assertEqual(self.kvstore.get(im), None)
        self.kvstore.set(im)
        self.assertEqual(im.size, [500, 500])

    def test_cleanup1(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.kvstore.delete_thumbnails(im)
        th = self.backend.get_thumbnail(im, '3x3')
        self.assertEqual(th.exists(), True)
        th.delete()
        self.assertEqual(th.exists(), False)
        self.assertEqual(self.kvstore.get(th).x, 3)
        self.assertEqual(self.kvstore.get(th).y, 3)
        self.kvstore.cleanup()
        self.assertEqual(self.kvstore.get(th), None)
        self.kvstore.delete(im)

    def test_cleanup2(self):
        self.kvstore.clear()
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        th3 = self.backend.get_thumbnail(im, '27x27')
        th4 = self.backend.get_thumbnail(im, '81x81')
        def keys_test(x, y, z):
            self.assertEqual(x, len(list(self.kvstore._find_keys(identity='image'))))
            self.assertEqual(y, len(list(self.kvstore._find_keys(identity='thumbnails'))))
            self.assertEqual(z, len(self.kvstore._get(im.key, identity='thumbnails') or []))
        keys_test(3, 1, 2)
        th3.delete()
        keys_test(3, 1, 2)
        self.kvstore.cleanup()
        keys_test(2, 1, 1)
        th4.delete()
        keys_test(2, 1, 1)
        self.kvstore.cleanup()
        keys_test(1, 0, 0)
        self.kvstore.clear()
        keys_test(0, 0, 0)

    def test_storage_serialize(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.assertEqual(im.serialize_storage(), 'thumbnail_tests.storage.TestStorage')
        self.assertEqual(
            ImageFile('http://www.image.jpg').serialize_storage(),
            'sorl.thumbnail.images.UrlStorage',
            )
        self.assertEqual(
            ImageFile('http://www.image.jpg', default.storage).serialize_storage(),
            'thumbnail_tests.storage.TestStorage',
            )
        self.assertEqual(
            ImageFile('getit', default_storage).serialize_storage(),
            'thumbnail_tests.storage.TestStorage',
            )

    def test_quality(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        th = self.backend.get_thumbnail(im, '100x100', quality=50)
        p1 = Popen(['identify', '-verbose', th.storage.path(th.name)], stdout=PIPE)
        p2 = Popen(['grep', '-c', 'Quality: 50'], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        output = p2.communicate()[0].strip()
        self.assertEqual(output, '1')

    def test_image_file_deserialize(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        default.kvstore.set(im)
        self.assertEqual(
            default.kvstore.get(im).serialize_storage(),
            'thumbnail_tests.storage.TestStorage',
            )
        im = ImageFile('http://www.aino.se/media/i/logo.png')
        default.kvstore.set(im)
        self.assertEqual(
            default.kvstore.get(im).serialize_storage(),
            'sorl.thumbnail.images.UrlStorage',
            )

    def test_abspath(self):
        item = Item.objects.get(image='500x500.jpg')
        image = ImageFile(item.image.path)
        val = render_to_string('thumbnail20.html', {
            'image': image,
        }).strip()
        im = self.backend.get_thumbnail(image, '32x32', crop='center')
        self.assertEqual('<img src="%s">' % im.url, val)


class TemplateTestCaseA(SimpleTestCaseBase):
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

    def test_nested(self):
        item = Item.objects.get(image='500x500.jpg')
        val = render_to_string('thumbnail6.html', {
            'item': item,
        }).strip()
        self.assertEqual(val, ('<a href="/media/test/cache/ee/75/ee75afefa6c50e2bb69040bd230adb8c.jpg">'
                               '<img src="/media/test/cache/f2/dd/f2ddc6972adc006de1635e4b30141267.jpg" width="400" height="400">'
                               '</a>'))

    def test_serialization_options(self):
        item = Item.objects.get(image='500x500.jpg')
        for j in xrange(0, 20):
            # we could be lucky...
            val0 = render_to_string('thumbnail7.html', {
                'item': item,
            }).strip()
            val1 = render_to_string('thumbnail7a.html', {
                'item': item,
            }).strip()
            self.assertEqual(val0, val1)

    def test_options(self):
        item = Item.objects.get(image='500x500.jpg')
        options = {
            'crop': "center",
            'upscale': True,
            'quality': 77,
        }
        val0 = render_to_string('thumbnail8.html', {
            'item': item,
            'options': options,
        }).strip()
        val1 = render_to_string('thumbnail8a.html', {
            'item': item,
        }).strip()
        self.assertEqual(val0, val1)

    def test_progressive(self):
        im = Item.objects.get(image='500x500.jpg').image
        th = self.backend.get_thumbnail(im, '100x100', progressive=True)
        path = pjoin(settings.MEDIA_ROOT, th.name)
        p = Popen(['identify', '-verbose', path], stdout=PIPE)
        p.wait()
        m = re.search('Interlace: JPEG', p.stdout.read())
        self.assertEqual(bool(m), True)

    def test_nonprogressive(self):
        im = Item.objects.get(image='500x500.jpg').image
        th = self.backend.get_thumbnail(im, '100x100', progressive=False)
        path = pjoin(settings.MEDIA_ROOT, th.name)
        p = Popen(['identify', '-verbose', path], stdout=PIPE)
        p.wait()
        m = re.search('Interlace: None', p.stdout.read())
        self.assertEqual(bool(m), True)

    def test_orientation(self):
        data_dir = pjoin(settings.MEDIA_ROOT, 'data')
        shutil.copytree(settings.DATA_ROOT, data_dir)
        ref = Image.open(pjoin(data_dir, '1_topleft.jpg'))
        top = ref.getpixel((14, 7))
        left = ref.getpixel((7, 14))
        engine = PILEngine()
        def epsilon(x, y):
            if isinstance(x, (tuple, list)):
                x = sum(x) / len(x)
            if isinstance(y, (tuple, list)):
                y = sum(y) / len(y)
            return abs(x - y)
        for name in sorted(os.listdir(data_dir)):
            th = self.backend.get_thumbnail('data/%s' % name, '30x30')
            im = engine.get_image(th)
            self.assertLess(epsilon(top, im.getpixel((14, 7))), 10)
            self.assertLess(epsilon(left, im.getpixel((7, 14))), 10)
            exif = im._getexif()
            if exif:
                self.assertEqual(exif.get(0x0112), 1)


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
        self.assertEqual(val, '<img src="/media/test/cache/11/b5/11b5d54b6ab2c9cda20a064153f90d2f.jpg" width="1985" height="666" class="landscape">')

    def testEmpty(self):
        val = render_to_string('thumbnail5.html', {}).strip()
        self.assertEqual(val, '<p>empty</p>')


class TemplateTestCaseClient(unittest.TestCase):
    def setUp(self):
        self.org_settings = {}
        params = {
            'THUMBNAIL_DEBUG': False,
        }
        for k, v in params.iteritems():
            self.org_settings[k] = getattr(settings, k)
            setattr(settings, k, v)

    def testEmptyError(self):
        client = Client()
        response = client.get('/thumbnail9.html')
        self.assertEqual(response.content.strip(), '<p>empty</p>')
        from django.core.mail import outbox
        self.assertEqual(outbox[0].subject, '[sorl-thumbnail] ERROR: /thumbnail9.html')
        end = outbox[0].body.split('\n\n')[-2][-20:-1]
        self.assertEqual(end, 'tests/media/invalid')

    def tearDown(self):
        for k, v in self.org_settings.iteritems():
            setattr(settings, k, v)


class CropTestCase(unittest.TestCase):
    def setUp(self):
        self.backend = get_module_class(settings.THUMBNAIL_BACKEND)()
        self.engine = get_module_class(settings.THUMBNAIL_ENGINE)()
        self.kvstore = get_module_class(settings.THUMBNAIL_KVSTORE)()
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        # portrait
        name = 'portrait.jpg'
        fn = pjoin(settings.MEDIA_ROOT, name)
        im = Image.new('L', (100, 200))
        im.paste(255, (0, 0, 100, 100))
        im.save(fn)
        self.portrait = ImageFile(Item.objects.get_or_create(image=name)[0].image)
        self.kvstore.delete(self.portrait)

        # landscape
        name = 'landscape.jpg'
        fn = pjoin(settings.MEDIA_ROOT, name)
        im = Image.new('L', (200, 100))
        im.paste(255, (0, 0, 100, 100))
        im.save(fn)
        self.landscape = ImageFile(Item.objects.get_or_create(image=name)[0].image)
        self.kvstore.delete(self.landscape)

    def testPortraitCrop(self):
        def mean_pixel(x, y):
            values = im.getpixel((x, y))
            if not isinstance(values, (tuple, list)):
                values = [values]
            return reduce(operator.add, values) / len(values)
        for crop in ('center', '88% 50%', '50px'):
            th = self.backend.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            self.assertEqual(mean_pixel(50,0), 255)
            self.assertEqual(mean_pixel(50,45), 255)
            self.assertEqual(250 < mean_pixel(50,49) <= 255, True)
            self.assertEqual(mean_pixel(50,55), 0)
            self.assertEqual(mean_pixel(50,99), 0)
        for crop in ('top', '0%', '0px'):
            th = self.backend.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            for x in xrange(0, 99, 10):
                for y in xrange(0, 99, 10):
                    self.assertEqual(250 < mean_pixel(x, y) <= 255, True)
        for crop in ('bottom', '100%', '100px'):
            th = self.backend.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = PILEngine()
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
            engine = PILEngine()
            im = engine.get_image(th)
            self.assertEqual(mean_pixel(0, 50), 255)
            self.assertEqual(mean_pixel(45, 50), 255)
            self.assertEqual(250 < mean_pixel(49, 50) <= 255, True)
            self.assertEqual(mean_pixel(55, 50), 0)
            self.assertEqual(mean_pixel(99, 50), 0)
        for crop in ('left', '0%', '0px'):
            th = self.backend.get_thumbnail(self.landscape, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            for x in xrange(0, 99, 10):
                for y in xrange(0, 99, 10):
                    self.assertEqual(250 < mean_pixel(x, y) <= 255, True)
        for crop in ('right', '100%', '100px'):
            th = self.backend.get_thumbnail(self.landscape, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            for x in xrange(0, 99, 10):
                for y in xrange(0, 99, 10):
                    self.assertEqual(0 <= mean_pixel(x, y) < 5, True)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)


class DummyTestCase(unittest.TestCase):
    def setUp(self):
        self.backend = get_module_class(settings.THUMBNAIL_BACKEND)()
        self.org_settings = {}
        params = {
            'THUMBNAIL_DUMMY': True,
        }
        for k, v in params.iteritems():
            self.org_settings[k] = getattr(settings, k)
            setattr(settings, k, v)

    def test_dummy_tags(self):
        val = render_to_string('thumbnaild1.html', {
            'anything': 'AINO',
        }).strip()
        self.assertEqual(val, '<img style="margin:auto" width="200" height="100">')
        val = render_to_string('thumbnaild2.html', {
            'anything': None,
        }).strip()
        self.assertEqual(val, '<img src="http://dummyimage.com/300x200" width="300" height="200"><p>NOT</p>')
        val = render_to_string('thumbnaild3.html', {
        }).strip()
        self.assertEqual(val, '<img src="http://dummyimage.com/600x400" width="600" height="400">')

    def tearDown(self):
        for k, v in self.org_settings.iteritems():
            setattr(settings, k, v)


class ModelTestCase(SimpleTestCaseBase):
    def test_field1(self):
        self.kvstore.clear()
        item = Item.objects.get(image='100x100.jpg')
        im = ImageFile(item.image)
        self.assertEqual(None, self.kvstore.get(im))
        self.backend.get_thumbnail(im, '27x27')
        self.backend.get_thumbnail(im, '81x81')
        self.assertNotEqual(None, self.kvstore.get(im))
        self.assertEqual(3, len(list(self.kvstore._find_keys(identity='image'))))
        self.assertEqual(1, len(list(self.kvstore._find_keys(identity='thumbnails'))))


class BackendTest(SimpleTestCaseBase):
    def test_delete(self):
        im1 = Item.objects.get(image='100x100.jpg').image
        im2 = Item.objects.get(image='500x500.jpg').image
        default.kvstore.get_or_set(ImageFile(im1))
        # exists in kvstore and in storage 
        self.assertTrue(bool(default.kvstore.get(ImageFile(im1))))
        self.assertTrue(ImageFile(im1).exists())
        # delete
        delete(im1)
        self.assertFalse(bool(default.kvstore.get(ImageFile(im1))))
        self.assertFalse(ImageFile(im1).exists())

        default.kvstore.get_or_set(ImageFile(im2))
        # exists in kvstore and in storage 
        self.assertTrue(bool(default.kvstore.get(ImageFile(im2))))
        self.assertTrue(ImageFile(im2).exists())
        # delete
        delete(im2, delete_file=False)
        self.assertFalse(bool(default.kvstore.get(ImageFile(im2))))
        self.assertTrue(ImageFile(im2).exists())

class TestInputCase(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        self.name = u'åäö.jpg'
        fn = pjoin(settings.MEDIA_ROOT, self.name)
        im = Image.new('L', (666, 666))
        im.save(fn)

    def test_nonascii(self):
        # also test the get_thumbnail shortcut
        th = get_thumbnail(self.name, '200x200')
        self.assertEqual(
            th.url,
            '/media/test/cache/e7/2b/e72b64151559ea9c5cdd6aefc626bb7f.jpg'
            )

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

