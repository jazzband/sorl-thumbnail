# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import unittest
from subprocess import Popen, PIPE

import pytest
from PIL import Image
from django.core.files.storage import default_storage
from django.template.loader import render_to_string

from sorl.thumbnail import default
from sorl.thumbnail.base import ThumbnailBackend
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.parsers import parse_geometry
from sorl.thumbnail.templatetags.thumbnail import margin
from sorl.thumbnail.engines.pil_engine import Engine as PILEngine
from .models import Item
from .compat import is_osx
from .utils import BaseTestCase


pytestmark = pytest.mark.django_db


class SimpleTestCase(BaseTestCase):
    def test_simple(self):
        item = Item.objects.get(image='500x500.jpg')

        t = self.BACKEND.get_thumbnail(item.image, '400x300', crop='center')

        self.assertEqual(t.x, 400)
        self.assertEqual(t.y, 300)

        t = self.BACKEND.get_thumbnail(item.image, '1200x900', crop='13% 89%')

        self.assertEqual(t.x, 1200)
        self.assertEqual(t.y, 900)

    def test_upscale(self):
        item = Item.objects.get(image='100x100.jpg')

        t = self.BACKEND.get_thumbnail(item.image, '400x300', upscale=False)

        self.assertEqual(t.x, 100)
        self.assertEqual(t.y, 100)

        t = self.BACKEND.get_thumbnail(item.image, '400x300', upscale=True)

        self.assertEqual(t.x, 300)
        self.assertEqual(t.y, 300)

    def test_upscale_and_crop(self):
        item = Item.objects.get(image='200x100.jpg')

        t = self.BACKEND.get_thumbnail(item.image, '400x300', crop='center', upscale=False)

        self.assertEqual(t.x, 200)
        self.assertEqual(t.y, 100)

        t = self.BACKEND.get_thumbnail(item.image, '400x300', crop='center', upscale=True)
        self.assertEqual(t.x, 400)
        self.assertEqual(t.y, 300)

    def test_kvstore(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.KVSTORE.delete_thumbnails(im)
        th1 = self.BACKEND.get_thumbnail(im, '50')
        th2 = self.BACKEND.get_thumbnail(im, 'x50')
        th3 = self.BACKEND.get_thumbnail(im, '20x20')
        self.assertEqual(
            set([th1.key, th2.key, th3.key]),
            set(self.KVSTORE._get(im.key, identity='thumbnails'))
        )
        self.KVSTORE.delete_thumbnails(im)
        self.assertEqual(
            None,
            self.KVSTORE._get(im.key, identity='thumbnails')
        )

    def test_is_portrait(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        th = self.BACKEND.get_thumbnail(im, '50x200', crop='center')
        self.assertEqual(th.is_portrait(), True)
        th = self.BACKEND.get_thumbnail(im, '500x2', crop='center')
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
        self.KVSTORE.delete(im)
        self.assertEqual(self.KVSTORE.get(im), None)
        self.KVSTORE.set(im)
        self.assertEqual(im.size, [500, 500])

    def test_cleanup1(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.KVSTORE.delete_thumbnails(im)
        th = self.BACKEND.get_thumbnail(im, '3x3')
        self.assertEqual(th.exists(), True)
        th.delete()
        self.assertEqual(th.exists(), False)
        self.assertEqual(self.KVSTORE.get(th).x, 3)
        self.assertEqual(self.KVSTORE.get(th).y, 3)
        self.KVSTORE.cleanup()
        self.assertEqual(self.KVSTORE.get(th), None)
        self.KVSTORE.delete(im)

    def test_cleanup2(self):
        self.KVSTORE.clear()
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        th3 = self.BACKEND.get_thumbnail(im, '27x27')
        th4 = self.BACKEND.get_thumbnail(im, '81x81')

        def keys_test(x, y, z):
            self.assertEqual(x, len(list(self.KVSTORE._find_keys(identity='image'))))
            self.assertEqual(y, len(list(self.KVSTORE._find_keys(identity='thumbnails'))))
            self.assertEqual(z, len(self.KVSTORE._get(im.key, identity='thumbnails') or []))

        keys_test(3, 1, 2)
        th3.delete()
        keys_test(3, 1, 2)
        self.KVSTORE.cleanup()
        keys_test(2, 1, 1)
        th4.delete()
        keys_test(2, 1, 1)
        self.KVSTORE.cleanup()
        keys_test(1, 0, 0)
        self.KVSTORE.clear()
        keys_test(0, 0, 0)

    def test_clear_doesnt_regenerate(self):
        self.KVSTORE.clear()
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        th = self.BACKEND.get_thumbnail(im, '27x27')
        th_name_orig = self.KVSTORE.get(th).name
        self.KVSTORE.clear()
        th = self.BACKEND.get_thumbnail(im, '27x27')
        th_name_new = self.KVSTORE.get(th).name
        self.assertEqual(
            th_name_orig,
            th_name_new,
        )

    def test_storage_serialize(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        self.assertEqual(im.serialize_storage(), 'tests.thumbnail_tests.storage.TestStorage')
        self.assertEqual(
            ImageFile('http://www.image.jpg').serialize_storage(),
            'sorl.thumbnail.images.UrlStorage',
        )
        self.assertEqual(
            ImageFile('http://www.image.jpg', default.storage).serialize_storage(),
            'tests.thumbnail_tests.storage.TestStorage',
        )
        self.assertEqual(
            ImageFile('getit', default_storage).serialize_storage(),
            'tests.thumbnail_tests.storage.TestStorage',
        )

    @unittest.skipIf(is_osx(), 'quality is saved a different way on os x')
    def test_quality(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        th = self.BACKEND.get_thumbnail(im, '100x100', quality=50)
        p1 = Popen(['identify', '-verbose', th.storage.path(th.name)], stdout=PIPE)
        p2 = Popen(['grep', '-c', 'Quality: 50'], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        output = p2.communicate()[0].strip()
        self.assertEqual(output.decode('utf-8'), '1')

    def test_transparency(self):
        item, _created = self.create_image(
            '50x50_transparent.png', (50, 50), transparent=True)
        th = self.BACKEND.get_thumbnail(item.image, '11x11', format='PNG')
        img = Image.open(th.storage.path(th.name))
        self.assertTrue(self.is_transparent(img))

    def test_image_file_deserialize(self):
        im = ImageFile(Item.objects.get(image='500x500.jpg').image)
        default.kvstore.set(im)
        self.assertEqual(
            default.kvstore.get(im).serialize_storage(),
            'tests.thumbnail_tests.storage.TestStorage',
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
        val = render_to_string('thumbnail20.html', {'image': image, }).strip()

        im = self.BACKEND.get_thumbnail(image, '32x32', crop='center')
        self.assertEqual('<img src="%s">' % im.url, val)

    def test_new_tag_style(self):
        item = Item.objects.get(image='500x500.jpg')
        image = ImageFile(item.image.path)
        val = render_to_string('thumbnail20a.html', {'image': image, }).strip()

        im = self.BACKEND.get_thumbnail(image, '32x32', crop='center')
        self.assertEqual('<img src="%s">' % im.url, val)

    def test_relative_absolute_same_key(self):
        image = Item.objects.get(image='500x500.jpg').image
        imref1 = ImageFile(image.name)
        imref2 = ImageFile(os.path.join(settings.MEDIA_ROOT, image.name))
        self.assertEqual(imref1.key, imref2.key)

        self.create_image('medialibrary.jpg', (100, 100))
        image = Item.objects.get(image='medialibrary.jpg').image
        imref1 = ImageFile(image.name)
        imref2 = ImageFile(os.path.join(settings.MEDIA_ROOT, image.name))
        self.assertEqual(imref1.key, imref2.key)

        self.create_image('mediaäöü.jpg', (100, 100))
        image = Item.objects.get(image='mediaäöü.jpg').image
        imref1 = ImageFile(image.name)
        imref2 = ImageFile(os.path.join(settings.MEDIA_ROOT, image.name))
        self.assertEqual(imref1.key, imref2.key)


class CropTestCase(BaseTestCase):
    def setUp(self):
        super(CropTestCase, self).setUp()

        # portrait
        name = 'portrait.jpg'
        fn = os.path.join(settings.MEDIA_ROOT, name)
        im = Image.new('L', (100, 200))
        im.paste(255, (0, 0, 100, 100))
        im.save(fn)
        self.portrait = ImageFile(Item.objects.get_or_create(image=name)[0].image)
        self.KVSTORE.delete(self.portrait)

        # landscape
        name = 'landscape.jpg'
        fn = os.path.join(settings.MEDIA_ROOT, name)
        im = Image.new('L', (200, 100))
        im.paste(255, (0, 0, 100, 100))
        im.save(fn)
        self.landscape = ImageFile(Item.objects.get_or_create(image=name)[0].image)
        self.KVSTORE.delete(self.landscape)

    def test_portrait_crop(self):
        def mean_pixel(x, y):
            values = im.getpixel((x, y))
            if not isinstance(values, (tuple, list)):
                values = [values]
            return sum(values) / len(values)

        for crop in ('center', '88% 50%', '50px'):
            th = self.BACKEND.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)

            self.assertEqual(mean_pixel(50, 0), 255)
            self.assertEqual(mean_pixel(50, 45), 255)
            self.assertEqual(250 <= mean_pixel(50, 49) <= 255, True, mean_pixel(50, 49))
            self.assertEqual(mean_pixel(50, 55), 0)
            self.assertEqual(mean_pixel(50, 99), 0)

        for crop in ('top', '0%', '0px'):
            th = self.BACKEND.get_thumbnail(self.portrait, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            for x in range(0, 99, 10):
                for y in range(0, 99, 10):
                    self.assertEqual(250 < mean_pixel(x, y) <= 255, True)

        for crop in ('bottom', '100%', '100px'):
            th = self.BACKEND.get_thumbnail(self.portrait, '100x100', crop=crop)
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
            th = self.BACKEND.get_thumbnail(self.landscape, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)

            self.assertEqual(mean_pixel(0, 50), 255)
            self.assertEqual(mean_pixel(45, 50), 255)
            self.assertEqual(250 < mean_pixel(49, 50) <= 255, True)
            self.assertEqual(mean_pixel(55, 50), 0)
            self.assertEqual(mean_pixel(99, 50), 0)

        for crop in ('left', '0%', '0px'):
            th = self.BACKEND.get_thumbnail(self.landscape, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            for x in range(0, 99, 10):
                for y in range(0, 99, 10):
                    self.assertEqual(250 < mean_pixel(x, y) <= 255, True)

        for crop in ('right', '100%', '100px'):
            th = self.BACKEND.get_thumbnail(self.landscape, '100x100', crop=crop)
            engine = PILEngine()
            im = engine.get_image(th)
            coords = ((x, y) for y in range(0, 99, 10) for x in range(0, 99, 10))

            for x, y in coords:
                self.assertEqual(0 <= mean_pixel(x, y) < 5, True)

    def test_smart_crop(self):
        # TODO: Complete test for smart crop
        self.BACKEND.get_thumbnail('32x32', 'data/white_border.jpg', crop='smart')

    @unittest.skipIf(
        'pil_engine' not in settings.THUMBNAIL_ENGINE,
        'the other engines fail this test',
    )
    def test_image_with_orientation(self):
        name = 'data/aspect_test.jpg'
        item, _ = Item.objects.get_or_create(image=name)

        im = ImageFile(item.image)
        th = self.BACKEND.get_thumbnail(im, '50x50')

        # this is a 100x200 image with orientation 6 (90 degrees CW rotate)
        # the thumbnail should end up 25x50
        self.assertEqual(th.x, 25)
        self.assertEqual(th.y, 50)

    def test_crop_image_with_icc_profile(self):
        name = 'data/icc_profile_test.jpg'
        item, _ = Item.objects.get_or_create(image=name)

        im = ImageFile(item.image)
        th = self.BACKEND.get_thumbnail(im, '100x100')

        engine = PILEngine()

        self.assertEqual(
            engine.get_image(im).info.get('icc_profile'),
            engine.get_image(th).info.get('icc_profile')
        )


class DummyTestCase(unittest.TestCase):
    def setUp(self):
        self.BACKEND = get_module_class(settings.THUMBNAIL_BACKEND)()

    def tearDown(self):
        super(DummyTestCase, self).tearDown()
        settings.THUMBNAIL_ALTERNATIVE_RESOLUTIONS = []

    def test_dummy_tags(self):
        settings.THUMBNAIL_DUMMY = True

        val = render_to_string('thumbnaild1.html', {'anything': 'AINO', }).strip()
        self.assertEqual(val, '<img style="margin:auto" width="200" height="100">')
        val = render_to_string('thumbnaild2.html', {'anything': None, }).strip()
        self.assertEqual(
            val,
            '<img src="http://dummyimage.com/300x200" width="300" height="200"><p>NOT</p>'
        )
        val = render_to_string('thumbnaild3.html', {}).strip()
        self.assertEqual(val, '<img src="http://dummyimage.com/600x400" width="600" height="400">')

        settings.THUMBNAIL_DUMMY = False

    def test_alternative_resolutions(self):
        settings.THUMBNAIL_DUMMY = True
        settings.THUMBNAIL_ALTERNATIVE_RESOLUTIONS = [1.5, 2]
        val = render_to_string('thumbnaild4.html', {}).strip()
        self.assertEqual(
            val,
            '<img src="http://dummyimage.com/600x400" width="600" '
            'height="400" srcset="http://dummyimage.com/1200x800 2x; '
            'http://dummyimage.com/900x600 1.5x">'
        )


class ImageValidationTestCase(unittest.TestCase):
    def setUp(self):
        self.BACKEND = get_module_class(settings.THUMBNAIL_BACKEND)()

    @unittest.skip("See issue #427")
    def test_truncated_validation(self):
        """
        Test that is_valid_image returns false for a truncated image.
        """
        name = 'data/broken.jpeg'
        with open(name, 'rb') as broken_jpeg:
            data = broken_jpeg.read()

        engine = PILEngine()

        self.assertFalse(engine.is_valid_image(data))

    @unittest.skip("See issue #427. This seems to not-fail with wand")
    def test_truncated_generation_failure(self):
        """
        Confirm that generating a thumbnail for our "broken" image fails.
        """
        name = 'data/broken.jpeg'
        with open(name, 'rb') as broken_jpeg:

            with self.assertRaises((OSError, IOError,)):
                im = default.engine.get_image(broken_jpeg)

                options = ThumbnailBackend.default_options
                ratio = default.engine.get_image_ratio(im, options)
                geometry = parse_geometry('120x120', ratio)
                default.engine.create(im, geometry, options)
