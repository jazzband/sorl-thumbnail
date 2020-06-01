from io import StringIO
import os
import platform
import sys
import shutil
import unittest
from PIL import Image

import pytest
from django.test import TestCase
from django.test.utils import override_settings

from sorl.thumbnail import default, delete, get_thumbnail
from sorl.thumbnail.base import ThumbnailBackend
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class
from sorl.thumbnail.images import ImageFile
from .utils import BaseTestCase, FakeFile, same_open_fd_count
from .models import Item


pytestmark = pytest.mark.django_db


class BackendTest(BaseTestCase):
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


@override_settings(THUMBNAIL_PRESERVE_FORMAT=True, THUMBNAIL_FORMAT='XXX')
class PreserveFormatTest(TestCase):
    def setUp(self):
        self.backend = ThumbnailBackend()

    def test_with_various_formats(self):
        self.assertEqual(self.backend._get_format(FakeFile('foo.jpg')), 'JPEG')
        self.assertEqual(self.backend._get_format(FakeFile('foo.jpeg')), 'JPEG')
        self.assertEqual(self.backend._get_format(FakeFile('foo.png')), 'PNG')
        self.assertEqual(self.backend._get_format(FakeFile('foo.gif')), 'GIF')

    def test_double_extension(self):
        self.assertEqual(self.backend._get_format(FakeFile('foo.ext.jpg')), 'JPEG')

    def test_that_capitalization_doesnt_matter(self):
        self.assertEqual(self.backend._get_format(FakeFile('foo.PNG')), 'PNG')
        self.assertEqual(self.backend._get_format(FakeFile('foo.JPG')), 'JPEG')

    def test_fallback_format(self):
        self.assertEqual(self.backend._get_format(FakeFile('foo.txt')), 'XXX')

    def test_with_nonascii(self):
        self.assertEqual(self.backend._get_format(FakeFile('你好.jpg')), 'JPEG')

    def test_image_remote_url(self):
        self.assertEqual(self.backend._get_format(FakeFile('http://example.com/1.png')), 'PNG')


@unittest.skipIf(platform.system() == "Windows", "Can't easily count descriptors on windows")
class TestDescriptors(unittest.TestCase):
    """Make sure we're not leaving open descriptors on file exceptions"""
    ENGINE = None

    def setUp(self):
        self.ENGINE = get_module_class(settings.THUMBNAIL_ENGINE)()

    def test_no_source_get_image(self):
        """If source image does not exists, properly close all file descriptors"""
        source = ImageFile('nonexistent.jpeg')

        with same_open_fd_count(self):
            with self.assertRaises(IOError):
                self.ENGINE.get_image(source)

    def test_is_valid_image(self):
        with same_open_fd_count(self):
            self.ENGINE.is_valid_image(b'invalidbinaryimage.jpg')

    @unittest.skipIf('pgmagick_engine' in settings.THUMBNAIL_ENGINE and sys.version_info.major == 2,
                     'No output has been received in the last 10 minutes,'
                     'this potentially indicates something wrong with the build itself.')
    def test_write(self):
        with same_open_fd_count(self):
            with self.assertRaises(Exception):
                self.ENGINE.write(image=self.ENGINE.get_image(StringIO(b'xxx')),
                                  options={'format': 'JPEG', 'quality': 90, 'image_info': {}},
                                  thumbnail=ImageFile('whatever_thumb.jpg', default.storage))


class ModelTestCase(BaseTestCase):
    def test_field1(self):
        self.KVSTORE.clear()
        item = Item.objects.get(image='100x100.jpg')
        im = ImageFile(item.image)
        self.assertEqual(None, self.KVSTORE.get(im))
        self.BACKEND.get_thumbnail(im, '27x27')
        self.BACKEND.get_thumbnail(im, '81x81')
        self.assertNotEqual(None, self.KVSTORE.get(im))
        self.assertEqual(3, len(list(self.KVSTORE._find_keys(identity='image'))))
        self.assertEqual(1, len(list(self.KVSTORE._find_keys(identity='thumbnails'))))


class TestInputCase(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        self.name = 'åäö.jpg'

        fn = os.path.join(settings.MEDIA_ROOT, self.name)
        im = Image.new('L', (666, 666))
        im.save(fn)

    def test_nonascii(self):
        # also test the get_thumbnail shortcut
        th = get_thumbnail(self.name, '200x200')
        self.assertEqual(th.url, '/media/test/cache/f5/26/f52608b56718f62abc45a90ff9459f2c.jpg')

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
