import os

from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.conf import settings
from sorl.thumbnail.engines.pil_engine import Engine as PILEngine
from sorl.thumbnail.images import ImageFile

from .utils import BaseStorageTestCase


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

        cache_path = "test/cache/2c/0f/2c0f909d420e760b8dc4e1d1f79e705b"
        actions = [
            f"exists: {cache_path}.jpg",

            # save regular resolution, same as in StorageTestCase
            "open: retina.jpg",
            f"save: {cache_path}.jpg",
            f"get_available_name: {cache_path}.jpg",
            f"exists: {cache_path}.jpg",

            # save the 1.5x resolution version
            f"save: {cache_path}@1.5x.jpg",
            f"get_available_name: {cache_path}@1.5x.jpg",
            f"exists: {cache_path}@1.5x.jpg",

            # save the 2x resolution version
            f"save: {cache_path}@2x.jpg",
            f"get_available_name: {cache_path}@2x.jpg",
            f"exists: {cache_path}@2x.jpg"
        ]
        self.assertEqual(self.log, actions)

        path = os.path.join(settings.MEDIA_ROOT, f"{cache_path}@1.5x.jpg")

        with open(path) as fp:
            engine = PILEngine()
            self.assertEqual(engine.get_image_size(engine.get_image(ImageFile(file_=fp))), (75, 75))
