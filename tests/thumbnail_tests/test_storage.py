# -*- coding: utf-8 -*-
import unittest
import pytest

from sorl.thumbnail import get_thumbnail, default
from sorl.thumbnail.helpers import get_module_class

from .utils import BaseStorageTestCase


pytestmark = pytest.mark.django_db


class StorageTestCase(BaseStorageTestCase):
    name = 'org.jpg'

    def test_new(self):
        get_thumbnail(self.image, '50x50')
        actions = [
            'exists: test/cache/ca/1a/ca1afb02b7250c125d8830c0e8a492ad.jpg',
            # open the original for thumbnailing
            'open: org.jpg',
            # save the file
            'save: test/cache/ca/1a/ca1afb02b7250c125d8830c0e8a492ad.jpg',
            # check for filename
            'get_available_name: test/cache/ca/1a/ca1afb02b7250c125d8830c0e8a492ad.jpg',
            # called by get_available_name
            'exists: test/cache/ca/1a/ca1afb02b7250c125d8830c0e8a492ad.jpg',
        ]
        self.assertEqual(self.log, actions)

    def test_cached(self):
        get_thumbnail(self.image, '50x50')
        self.assertEqual(self.log, [])  # now this should all be in cache

    def test_safe_methods(self):
        im = default.kvstore.get(self.image)
        url, x, y = (im.url, im.x, im.y)
        self.assertEqual(self.log, [])


class UrlStorageTestCase(unittest.TestCase):
    def test_encode_utf8_filenames(self):
        storage = get_module_class('sorl.thumbnail.images.UrlStorage')()
        self.assertEqual(
            storage.normalize_url('El jovencito emponzoñado de whisky, qué figura exhibe'),
            'El%20jovencito%20emponzoado%20de%20whisky%2C%20qu%20figura%20exhibe'
        )

