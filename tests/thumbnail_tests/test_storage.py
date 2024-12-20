import unittest

from django.test.utils import override_settings

from sorl.thumbnail import default, get_thumbnail
from sorl.thumbnail.helpers import get_module_class

from .utils import BaseStorageTestCase


class StorageTestCase(BaseStorageTestCase):
    name = 'org.jpg'

    def test_new(self):
        get_thumbnail(self.image, '50x50')
        actions = [
            'exists: test/cache/45/bb/45bbbdab11e235a80e603aa119e8786b.jpg',
            # open the original for thumbnailing
            'open: org.jpg',
            # save the file
            'save: test/cache/45/bb/45bbbdab11e235a80e603aa119e8786b.jpg',
            # check for filename
            'get_available_name: test/cache/45/bb/45bbbdab11e235a80e603aa119e8786b.jpg',
            # called by get_available_name
            'exists: test/cache/45/bb/45bbbdab11e235a80e603aa119e8786b.jpg',
        ]
        self.assertEqual(self.log, actions)

    def test_cached(self):
        get_thumbnail(self.image, '100x50')
        self.log = []
        get_thumbnail(self.image, '100x50')
        self.assertEqual(self.log, [])  # now this should all be in cache

    def test_safe_methods(self):
        im = default.kvstore.get(self.image)
        self.assertIsNotNone(im.url)
        self.assertIsNotNone(im.x)
        self.assertIsNotNone(im.y)
        self.assertEqual(self.log, [])

    @override_settings(THUMBNAIL_STORAGE="tests.thumbnail_tests.storage.TestStorage")
    def test_storage_setting_as_path_to_class(self):
        storage = default.Storage()
        self.assertEqual(storage.__class__.__name__, "TestStorage")


class UrlStorageTestCase(unittest.TestCase):
    def test_encode_utf8_filenames(self):
        storage = get_module_class('sorl.thumbnail.images.UrlStorage')()
        self.assertEqual(
            storage.normalize_url('El jovencito emponzoñado de whisky, qué figura exhibe'),
            'El%20jovencito%20emponzoado%20de%20whisky%2C%20qu%20figura%20exhibe'
        )
