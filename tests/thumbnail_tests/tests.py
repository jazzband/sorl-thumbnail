# coding=utf-8
from __future__ import unicode_literals

import os
import re
import sys
import logging
import shutil
from os.path import join as pjoin
from subprocess import Popen, PIPE

from PIL import Image
from django.utils.six import StringIO
from django.core import management
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.test.client import Client

from django.utils import unittest
from django.test import TestCase
from django.test.utils import override_settings

from sorl.thumbnail import default, get_thumbnail, delete
from sorl.thumbnail.conf import settings
from sorl.thumbnail.engines.pil_engine import Engine as PILEngine
from sorl.thumbnail.helpers import get_module_class, ThumbnailError
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.log import ThumbnailLogHandler
from sorl.thumbnail.parsers import parse_crop, parse_geometry
from sorl.thumbnail.templatetags.thumbnail import margin

from sorl.thumbnail.base import ThumbnailBackend

from .models import Item
from .storage import slog, SlogHandler
from .compat import unittest, PY3
from .utils import same_open_fd_count

skip = unittest.skip
skipIf = unittest.skipIf

handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)


class StorageTestCase(unittest.TestCase):
    im = None

    def setUp(self):
        name = 'org.jpg'
        os.makedirs(settings.MEDIA_ROOT)
        fn = pjoin(settings.MEDIA_ROOT, name)
        Image.new('L', (100, 100)).save(fn)
        self.im = ImageFile(name)

    @skip('stall')
    def test_a_new(self):
        slog.start_log()
        get_thumbnail(self.im, '50x50')
        log = slog.stop_log()
        actions = [
            'open: org.jpg',  # open the original for thumbnailing
            # save the file
            'save: test/cache/ca/1a/ca1afb02b7250c125d8830c0e8a492ad.jpg',
            # check for filename
            'get_available_name: test/cache/ca/1a/ca1afb02b7250c125d8830c0e8a492ad.jpg',
            # called by get_available_name
            'exists: test/cache/ca/1a/ca1afb02b7250c125d8830c0e8a492ad.jpg',
        ]
        self.assertEqual(log, actions)

    @skip('stall')
    def test_b_cached(self):
        slog.start_log()
        get_thumbnail(self.im, '50x50')
        log = slog.stop_log()
        self.assertEqual(log, [])  # now this should all be in cache

    @skip('stall')
    def test_c_safe_methods(self):
        slog.start_log()
        im = default.kvstore.get(self.im)
        im.url, im.x, im.y
        log = slog.stop_log()
        self.assertEqual(log, [])

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)


class UrlStorageTestCase(unittest.TestCase):
    def test_encode_utf8_filenames(self):
        storage = get_module_class('sorl.thumbnail.images.UrlStorage')()
        self.assertEqual(
            storage.normalize_url('El jovencito emponzoñado de whisky, qué figura exhibe'),
            'El%20jovencito%20emponzoado%20de%20whisky%2C%20qu%20figura%20exhibe'
        )


class ParsersTestCase(unittest.TestCase):
    def test_alias_crop(self):
        crop = parse_crop('center', (500, 500), (400, 400))
        self.assertEqual(crop, (50, 50))
        crop = parse_crop('right', (500, 500), (400, 400))
        self.assertEqual(crop, (100, 50))

    def test_percent_crop(self):
        crop = parse_crop('50% 0%', (500, 500), (400, 400))
        self.assertEqual(crop, (50, 0))
        crop = parse_crop('10% 80%', (500, 500), (400, 400))
        self.assertEqual(crop, (10, 80))

    def test_px_crop(self):
        crop = parse_crop('200px 33px', (500, 500), (400, 400))
        self.assertEqual(crop, (100, 33))

    def test_bad_crop(self):
        self.assertRaises(ThumbnailError, parse_crop, '-200px', (500, 500), (400, 400))

    def test_geometry(self):
        g = parse_geometry('222x30')
        self.assertEqual(g, (222, 30))
        g = parse_geometry('222')
        self.assertEqual(g, (222, None))
        g = parse_geometry('x999')
        self.assertEqual(g, (None, 999))


class SimpleTestCaseBase(unittest.TestCase):
    backend = None
    engine = None
    kvstore = None

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
    def test_simple(self):
        item = Item.objects.get(image='500x500.jpg')

        t = self.backend.get_thumbnail(item.image, '400x300', crop='center')

        self.assertEqual(t.x, 400)
        self.assertEqual(t.y, 300)

        t = self.backend.get_thumbnail(item.image, '1200x900', crop='13% 89%')

        self.assertEqual(t.x, 1200)
        self.assertEqual(t.y, 900)

    def test_upscale(self):
        item = Item.objects.get(image='100x100.jpg')

        t = self.backend.get_thumbnail(item.image, '400x300', upscale=False)

        self.assertEqual(t.x, 100)
        self.assertEqual(t.y, 100)

        t = self.backend.get_thumbnail(item.image, '400x300', upscale=True)

        self.assertEqual(t.x, 300)
        self.assertEqual(t.y, 300)

    def test_upscale_and_crop(self):
        item = Item.objects.get(image='200x100.jpg')

        t = self.backend.get_thumbnail(item.image, '400x300', crop='center', upscale=False)

        self.assertEqual(t.x, 200)
        self.assertEqual(t.y, 100)


        t = self.backend.get_thumbnail(item.image, '400x300', crop='center', upscale=True)
        self.assertEqual(t.x, 400)
        self.assertEqual(t.y, 300)

    @skip('stall')
    def test_kvstore(self):
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

    @skip('stall')
    def test_is_portrait(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        th = self.backend.get_thumbnail(im, '50x200', crop='center')
        self.assertEqual(th.is_portrait(), True)
        th = self.backend.get_thumbnail(im, '500x2', crop='center')
        self.assertEqual(th.is_portrait(), False)

    def test_margin(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.assertEqual(margin(im, '1000x1000'), '250px 250px 250px 250px')
        self.assertEqual(margin(im, '800x1000'), '250px 150px 250px 150px')
        self.assertEqual(margin(im, '500x500'), '0px 0px 0px 0px')
        self.assertEqual(margin(im, '500x501'), '0px 0px 1px 0px')
        self.assertEqual(margin(im, '503x500'), '0px 2px 0px 1px')
        self.assertEqual(margin(im, '300x300'), '-100px -100px -100px -100px')

    def test_kvstore_get_and_set(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.kvstore.delete(im)
        self.assertEqual(self.kvstore.get(im), None)
        self.kvstore.set(im)
        self.assertEqual(im.size, [500, 500])

    @skip('stall')
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

    @skip('stall')
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

    @skipIf(sys.platform == 'darwin', 'quality is saved a different way on os x')
    def test_quality(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        th = self.backend.get_thumbnail(im, '100x100', quality=50)
        p1 = Popen(['identify', '-verbose', th.storage.path(th.name)], stdout=PIPE)
        p2 = Popen(['grep', '-c', 'Quality: 50'], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        output = p2.communicate()[0].strip()
        self.assertEqual(output.decode('utf-8'), '1')

    def test_image_file_deserialize(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        default.kvstore.set(im)
        self.assertEqual(
            default.kvstore.get(im).serialize_storage(),
            'thumbnail_tests.storage.TestStorage',
        )
        im = ImageFile('http://dummyimage.com/300x300/')
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

    def test_new_tag_style(self):
        item = Item.objects.get(image='500x500.jpg')
        image = ImageFile(item.image.path)
        val = render_to_string('thumbnail20a.html', {
            'image': image,
        }).strip()
        im = self.backend.get_thumbnail(image, '32x32', crop='center')
        self.assertEqual('<img src="%s">' % im.url, val)

    def test_html_filter(self):
        text = '<img alt="A image!" src="http://dummyimage.com/800x800" />'
        val = render_to_string('htmlfilter.html', {
            'text': text,
        }).strip()
        self.assertEqual('<img alt="A image!" src="/media/test/cache/2e/35/2e3517d8aa949728b1ee8b26c5a7bbc4.jpg" />', val)

    def test_markdown_filter(self):
        text = '![A image!](http://dummyimage.com/800x800)'
        val = render_to_string('markdownfilter.html', {
            'text': text,
        }).strip()
        self.assertEqual('![A image!](/media/test/cache/2e/35/2e3517d8aa949728b1ee8b26c5a7bbc4.jpg)', val)


class TemplateTestCaseA(SimpleTestCaseBase):
    @skip('evaluated as string')
    def test_model(self):
        item = Item.objects.get(image='500x500.jpg')
        val = render_to_string('thumbnail1.html', {
            'item': item,
        }).strip()
        self.assertEqual(val, '<img style="margin:0px 0px 0px 0px" width="200" height="100">')
        val = render_to_string('thumbnail2.html', {
            'item': item,
        }).strip()
        self.assertEqual(val, '<img style="margin:0px 50px 0px 50px" width="100" height="100">')

    def test_nested(self):
        item = Item.objects.get(image='500x500.jpg')
        val = render_to_string('thumbnail6.html', {
            'item': item,
        }).strip()
        self.assertEqual(val, (
            '<a href="/media/test/cache/ba/d7/bad785264867676a926566150f90f87c.jpg">'
            '<img src="/media/test/cache/c6/7a/c67a64c3145f8834cd6770f6f80198c9.jpg" width="400" height="400">'
            '</a>')
        )

    def test_serialization_options(self):
        item = Item.objects.get(image='500x500.jpg')

        for j in range(0, 20):
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
        m = re.search('Interlace: JPEG', str(p.stdout.read()))
        self.assertEqual(bool(m), True)

    def test_nonprogressive(self):
        im = Item.objects.get(image='500x500.jpg').image
        th = self.backend.get_thumbnail(im, '100x100', progressive=False)
        path = pjoin(settings.MEDIA_ROOT, th.name)
        p = Popen(['identify', '-verbose', path], stdout=PIPE)
        p.wait()
        m = re.search('Interlace: None', str(p.stdout.read()))
        self.assertEqual(bool(m), True)

    @skip('stall')
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

    @skip('stalling. It does not dowlonad the dummy image')
    def test_url(self):
        val = render_to_string('thumbnail3.html', {}).strip()
        self.assertEqual(val, '<img style="margin:0px 0px 0px 0px" width="20" height="20">')

    def test_portrait(self):
        val = render_to_string('thumbnail4.html', {
            'source': 'http://dummyimage.com/120x100/',
            'dims': 'x66',
        }).strip()
        self.assertEqual(val, '<img src="/media/test/cache/7b/cd/7bcd20922c6750649f431df7c3cdbc5e.jpg" width="79" height="66" class="landscape">')

    def test_empty(self):
        val = render_to_string('thumbnail5.html', {}).strip()
        self.assertEqual(val, '<p>empty</p>')


class TemplateTestCaseClient(TestCase):

    def test_empty_error(self):
        with self.settings(THUMBNAIL_DEBUG=False):
            from django.core.mail import outbox

            client = Client()
            response = client.get('/thumbnail9.html')
            self.assertEqual(response.content.strip(), b'<p>empty</p>')
            self.assertEqual(outbox[0].subject, '[sorl-thumbnail] ERROR: /thumbnail9.html')

            end = outbox[0].body.split('\n\n')[-2].split(':')[1].strip()

            self.assertEqual(end, '[Errno 2] No such file or directory')


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

    def test_portrait_crop(self):
        def mean_pixel(x, y):
            values = im.getpixel((x, y))
            if not isinstance(values, (tuple, list)):
                values = [values]
            return sum(values) / len(values)

        for crop in ('center', '88% 50%', '50px'):
            th = self.backend.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            self.assertEqual(mean_pixel(50, 0), 255)
            self.assertEqual(mean_pixel(50, 45), 255)
            self.assertEqual(250 <= mean_pixel(50, 49) <= 255, True, mean_pixel(50, 49))
            self.assertEqual(mean_pixel(50, 55), 0)
            self.assertEqual(mean_pixel(50, 99), 0)

        for crop in ('top', '0%', '0px'):
            th = self.backend.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            for x in range(0, 99, 10):
                for y in range(0, 99, 10):
                    self.assertEqual(250 < mean_pixel(x, y) <= 255, True)

        for crop in ('bottom', '100%', '100px'):
            th = self.backend.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            for x in range(0, 99, 10):
                for y in range(0, 99, 10):
                    self.assertEqual(0 <= mean_pixel(x, y) < 5, True)

    def test_landscape_crop(self):

        def mean_pixel(x, y):
            values = im.getpixel((x, y))
            if not isinstance(values, (tuple, list)):
                values = [values]
            return sum(values) / len(values)

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
            for x in range(0, 99, 10):
                for y in range(0, 99, 10):
                    self.assertEqual(250 < mean_pixel(x, y) <= 255, True)

        for crop in ('right', '100%', '100px'):
            th = self.backend.get_thumbnail(self.landscape, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            for x in range(0, 99, 10):
                for y in range(0, 99, 10):
                    self.assertEqual(0 <= mean_pixel(x, y) < 5, True)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)


class DummyTestCase(TestCase):
    def setUp(self):
        self.backend = get_module_class(settings.THUMBNAIL_BACKEND)()

    @skip('stalling')
    def test_dummy_tags(self):
        with self.settings(THUMBNAIL_DUMMY=True):
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


class ModelTestCase(SimpleTestCaseBase):

    @skip("Skip due 100% cpu usage without fail")
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

        self.name = 'åäö.jpg'

        fn = pjoin(settings.MEDIA_ROOT, self.name)
        im = Image.new('L', (666, 666))
        im.save(fn)

    @skipIf(PY3, 'hash is different')
    def test_nonascii(self):
        # also test the get_thumbnail shortcut
        th = get_thumbnail(self.name, '200x200')
        self.assertEqual(
            th.url,
            '/media/test/cache/8e/16/8e1629dd742c05fc3812ace2e7569f85.jpg'
        )

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)


@skipIf(sys.platform.startswith("win"), "Can't easily count descriptors on windows")
class TestDescriptors(unittest.TestCase):
    """Make sure we're not leaving open descriptors on file exceptions"""
    engine = None

    def setUp(self):
        self.engine = get_module_class(settings.THUMBNAIL_ENGINE)()

    def test_no_source_get_image(self):
        """If source image does not exists, properly close all file descriptors"""
        source = ImageFile('nonexistent.jpeg')

        with same_open_fd_count(self):
            with self.assertRaises(IOError):
                self.engine.get_image(source)

    def test_is_valid_image(self):
        with same_open_fd_count(self):
            self.engine.is_valid_image(b'invalidbinaryimage.jpg')

    @skipIf(os.environ.get('SETTINGS', None) == 'pgmagick' and  sys.version_info.major == 2,
            'No output has been received in the last 10 minutes, this potentially indicates something wrong with the build itself.')
    def test_write(self):
        with same_open_fd_count(self):
            with self.assertRaises(Exception):
                self.engine.write(image=self.engine.get_image(StringIO(b'xxx')),
                                  options={'format': 'JPEG', 'quality': 90, 'image_info': {}},
                                  thumbnail=ImageFile('whatever_thumb.jpg', default.storage))


class CommandTests(SimpleTestCase):

    def test_clear_action(self):
        out = StringIO()
        management.call_command('thumbnail', 'clear', verbosity=1, stdout=out)
        self.assertEqual(out.getvalue(), "Clear the Key Value Store ... [Done]\n")

    def test_cleanup_action(self):
        out = StringIO()
        management.call_command('thumbnail', 'cleanup', verbosity=1, stdout=out)
        self.assertEqual(out.getvalue(), "Cleanup thumbnails ... [Done]\n")


class FakeFile(object):
    """
    Used to test the _get_format method.
    """

    def __init__(self, name):
        self.name = name


@override_settings(THUMBNAIL_PRESERVE_FORMAT=True,
                   THUMBNAIL_FORMAT='XXX')
class PreserveFormatTest(TestCase):
    def setUp(self):
        self.backend = ThumbnailBackend()

    def test_with_various_formats(self):
        self.assertEqual(self.backend._get_format(FakeFile('foo.jpg')), 'JPEG')
        self.assertEqual(self.backend._get_format(FakeFile('foo.jpeg')), 'JPEG')
        self.assertEqual(self.backend._get_format(FakeFile('foo.png')), 'PNG')

    def test_double_extension(self):
        self.assertEqual(self.backend._get_format(FakeFile('foo.ext.jpg')), 'JPEG')

    def test_that_capitalization_doesnt_matter(self):
        self.assertEqual(self.backend._get_format(FakeFile('foo.PNG')), 'PNG')
        self.assertEqual(self.backend._get_format(FakeFile('foo.JPG')), 'JPEG')

    def test_fallback_format(self):
        self.assertEqual(self.backend._get_format(FakeFile('foo.txt')), 'XXX')

    def test_with_nonascii(self):
        self.assertEqual(self.backend._get_format(FakeFile('你好.jpg')), 'JPEG')
