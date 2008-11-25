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
extension_thumbnail = thumbnail.copy()
extension_thumbnail['extension'] = 'png'

# Temporary models for field_tests
class TestThumbnailFieldModel(models.Model):
    photo = ImageWithThumbnailsField(upload_to='test', thumbnail=thumbnail,
                                     extra_thumbnails=extra_thumbnails)


class TestThumbnailFieldExtensionModel(models.Model):
    photo = ImageWithThumbnailsField(upload_to='test',
                                     thumbnail=extension_thumbnail,
                                     extra_thumbnails=extra_thumbnails)


class FieldTest(BaseTest):
    def test_thumbnail(self):
        model = TestThumbnailFieldModel(photo=RELATIVE_PIC_NAME)
        thumb = model.photo.thumbnail
        tag = model.photo.thumbnail_tag
        expected_filename = os.path.join(settings.MEDIA_ROOT,
            'sorl-thumbnail-test_source_jpg_50x50_q85.jpg')
        self.verify_thumbnail((50, 37), thumb, expected_filename)
        expected_tag = '<img src="%s" width="50" height="37" alt="" />' % \
            '/'.join((settings.MEDIA_URL.rstrip('/'),
                      'sorl-thumbnail-test_source_jpg_50x50_q85.jpg'))
        self.assertEqual(tag, expected_tag)

    def test_extra_thumbnails(self):
        model = TestThumbnailFieldModel(photo=RELATIVE_PIC_NAME)
        self.assertTrue('admin' in model.photo.extra_thumbnails)
        thumb = model.photo.extra_thumbnails['admin']
        tag = model.photo.extra_thumbnails_tag['admin']
        expected_filename = os.path.join(settings.MEDIA_ROOT,
            'sorl-thumbnail-test_source_jpg_30x30_crop_q85.jpg')
        self.verify_thumbnail((30, 30), thumb, expected_filename)
        expected_tag = '<img src="%s" width="30" height="30" alt="" />' % \
            '/'.join((settings.MEDIA_URL.rstrip('/'),
                      'sorl-thumbnail-test_source_jpg_30x30_crop_q85.jpg'))
        self.assertEqual(tag, expected_tag)

    def test_extension(self):
        model = TestThumbnailFieldExtensionModel(photo=RELATIVE_PIC_NAME)
        thumb = model.photo.thumbnail
        tag = model.photo.thumbnail_tag
        expected_filename = os.path.join(settings.MEDIA_ROOT,
            'sorl-thumbnail-test_source_jpg_50x50_q85.png')
        self.verify_thumbnail((50, 37), thumb, expected_filename)
        expected_tag = '<img src="%s" width="50" height="37" alt="" />' % \
            '/'.join((settings.MEDIA_URL.rstrip('/'),
                      'sorl-thumbnail-test_source_jpg_50x50_q85.png'))
        self.assertEqual(tag, expected_tag)

    def test_delete_thumbnails(self):
        model = TestThumbnailFieldModel(photo=RELATIVE_PIC_NAME)
        thumb_file = model.photo.thumbnail.dest
        open(thumb_file, 'wb').close()
        self.assert_(os.path.exists(thumb_file))
        model.photo.delete(save=False)
        self.assert_(not os.path.exists(thumb_file))

