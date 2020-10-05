import os

import pytest

from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.conf import settings
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.engines.pil_engine import Engine as PILEngine

from .utils import BaseStorageTestCase


pytestmark = pytest.mark.django_db


class AlternativeResolutionsTest(BaseStorageTestCase):
    name = 'retina.jpg'

    def setUp(self):
        settings.THUMBNAIL_ALTERNATIVE_RESOLUTIONS = [1.5, 2]
        super().setUp()
        self.maxDiff = None

    def tearDown(self):
        super().tearDown()
        settings.THUMBNAIL_ALTERNATIVE_RESOLUTIONS = []

    def test_retina(self):
        get_thumbnail(self.image, '50x50')

        actions = [
            'exists: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d.jpg',

            # save regular resolution, same as in StorageTestCase
            'open: retina.jpg',
            'save: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d.jpg',
            'get_available_name: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d.jpg',
            'exists: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d.jpg',

            # save the 1.5x resolution version
            'save: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d@1.5x.jpg',
            'get_available_name: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d@1.5x.jpg',
            'exists: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d@1.5x.jpg',

            # save the 2x resolution version
            'save: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d@2x.jpg',
            'get_available_name: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d@2x.jpg',
            'exists: test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d@2x.jpg'
        ]
        self.assertEqual(self.log, actions)

        path = os.path.join(settings.MEDIA_ROOT,
                            'test/cache/91/bb/91bb06cf9169e4c52132bb113f2d4c0d@1.5x.jpg')

        with open(path) as fp:
            engine = PILEngine()
            self.assertEqual(engine.get_image_size(engine.get_image(ImageFile(file_=fp))), (75, 75))
