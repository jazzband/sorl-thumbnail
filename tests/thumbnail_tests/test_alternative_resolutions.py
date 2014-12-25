# -*- coding: utf-8 -*-
import os

import pytest
from django.conf import settings

from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.engines.pil_engine import Engine as PILEngine

from .utils import BaseStorageTestCase


pytestmark = pytest.mark.django_db


class AlternativeResolutionsTest(BaseStorageTestCase):
    name = 'retina.jpg'

    def setUp(self):
        settings.THUMBNAIL_ALTERNATIVE_RESOLUTIONS = [1.5, 2]
        super(AlternativeResolutionsTest, self).setUp()

    def tearDown(self):
        super(AlternativeResolutionsTest, self).tearDown()
        settings.THUMBNAIL_ALTERNATIVE_RESOLUTIONS = []

    def test_retina(self):
        get_thumbnail(self.image, '50x50')

        actions = [
            'exists: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19.jpg',

            # save regular resolution, same as in StorageTestCase
            'open: retina.jpg',
            'save: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19.jpg',
            'get_available_name: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19.jpg',
            'exists: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19.jpg',

            # save the 1.5x resolution version
            'save: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19@1.5x.jpg',
            'get_available_name: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19@1.5x.jpg',
            'exists: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19@1.5x.jpg',

            # save the 2x resolution version
            'save: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19@2x.jpg',
            'get_available_name: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19@2x.jpg',
            'exists: test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19@2x.jpg'
        ]
        self.assertEqual(self.log, actions)

        path = os.path.join(settings.MEDIA_ROOT, 'test/cache/19/10/1910dc350bbe9ee55fd9d8d3d5e38e19@1.5x.jpg')

        with open(path) as fp:
            engine = PILEngine()
            self.assertEqual(engine.get_image_size(engine.get_image(ImageFile(file_=fp))), (75, 75))

