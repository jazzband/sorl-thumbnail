import os.path

from django.db import models
from django.conf import settings

from sorl.thumbnail.fields import ImageWithThumbnailsField
from sorl.thumbnail.tests.base import BaseTest, RELATIVE_PIC_NAME

thumbnail = {
    'size': (50,50)
}
extra_thumbnails = {
    'admin': {
        'size': (30, 30),
        'options': ('crop',),
    }
}

# Temporary model for field_tests
class TestThumbnailFieldModel(models.Model):
    photo = ImageWithThumbnailsField(upload_to='test', thumbnail=thumbnail,
                                     extra_thumbnails=extra_thumbnails)

class FieldTest(BaseTest):
    def test_model(self):
        m = TestThumbnailFieldModel(photo=RELATIVE_PIC_NAME)
        self.assertTrue(hasattr(m, 'get_photo_thumbnail'))
        self.assertTrue(hasattr(m, 'get_photo_thumbnail_tag'))
        self.assertTrue(hasattr(m, 'get_photo_admin_thumbnail'))
        self.assertTrue(hasattr(m, 'get_photo_admin_thumbnail_tag'))
        thumb = m.get_photo_thumbnail()
        expected_filename = os.path.join(settings.MEDIA_ROOT,
            'sorl-thumbnail-test_source_jpg_50x50_q85.jpg')
        self.verify_thumbnail((50, 37), thumb, expected_filename)
        admin_tag = m.get_photo_admin_thumbnail_tag()
        expected_tag = '<img src="%s" width="30" height="30" alt="" />' % \
            '/'.join((settings.MEDIA_URL.rstrip('/'),
                      'sorl-thumbnail-test_source_jpg_30x30_crop_q85.jpg'))
        self.assertEqual(admin_tag, expected_tag)
