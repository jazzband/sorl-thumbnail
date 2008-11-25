import unittest
import os
import time

from PIL import Image
from django.conf import settings

from sorl.thumbnail.base import Thumbnail
from sorl.thumbnail.main import DjangoThumbnail, get_thumbnail_setting
from sorl.thumbnail.processors import dynamic_import, get_valid_options
from sorl.thumbnail.tests.base import BaseTest, RELATIVE_PIC_NAME, PIC_NAME, THUMB_NAME, PIC_SIZE


PROCESSORS = dynamic_import(get_thumbnail_setting('PROCESSORS'))
VALID_OPTIONS = get_valid_options(PROCESSORS)


class ThumbnailTest(BaseTest):
    def testThumbnails(self):
        # Thumbnail
        thumb = Thumbnail(source=PIC_NAME, dest=THUMB_NAME % 1,
                          requested_size=(240, 240))
        self.verify_thumbnail((240, 180), thumb)

        # Cropped thumbnail
        thumb = Thumbnail(source=PIC_NAME, dest=THUMB_NAME % 2,
                          requested_size=(240, 240), opts=['crop'])
        self.verify_thumbnail((240, 240), thumb)

        # Thumbnail with altered JPEG quality
        thumb = Thumbnail(source=PIC_NAME, dest=THUMB_NAME % 3,
                          requested_size=(240, 240), quality=95)
        self.verify_thumbnail((240, 180), thumb)

    def testRegeneration(self):
        # Create thumbnail
        thumb_name = THUMB_NAME % 4
        thumb_size = (240, 240)
        thumb = Thumbnail(source=PIC_NAME, dest=thumb_name,
                          requested_size=thumb_size)
        self.images_to_delete.add(thumb_name)
        thumb_mtime = os.path.getmtime(thumb_name)
        time.sleep(1)

        # Create another instance, shouldn't generate a new thumb
        thumb = Thumbnail(source=PIC_NAME, dest=thumb_name,
                          requested_size=thumb_size)
        self.assertEqual(os.path.getmtime(thumb_name), thumb_mtime)

        # Recreate the source image, then see if a new thumb is generated
        Image.new('RGB', PIC_SIZE).save(PIC_NAME, 'JPEG')
        thumb = Thumbnail(source=PIC_NAME, dest=thumb_name,
                          requested_size=thumb_size)
        self.assertNotEqual(os.path.getmtime(thumb_name), thumb_mtime)


class DjangoThumbnailTest(BaseTest):
    def setUp(self):
        super(DjangoThumbnailTest, self).setUp()
        # Add another source image in a sub-directory for testing subdir and
        # basedir.
        self.sub_dir = os.path.join(settings.MEDIA_ROOT, 'test_thumbnail')
        try:
            os.mkdir(self.sub_dir)
        except OSError:
            pass
        self.pic_subdir = os.path.join(self.sub_dir, RELATIVE_PIC_NAME)
        Image.new('RGB', PIC_SIZE).save(self.pic_subdir, 'JPEG')
        self.images_to_delete.add(self.pic_subdir)

    def testFilenameGeneration(self):
        basename = RELATIVE_PIC_NAME.replace('.', '_')
        # Basic filename
        thumb = DjangoThumbnail(relative_source=RELATIVE_PIC_NAME,
                                requested_size=(240, 120))
        expected = os.path.join(settings.MEDIA_ROOT, basename)
        expected += '_240x120_q85.jpg'
        self.verify_thumbnail((160, 120), thumb, expected_filename=expected)

        # Changed quality and cropped
        thumb = DjangoThumbnail(relative_source=RELATIVE_PIC_NAME,
                                requested_size=(240, 120), opts=['crop'],
                                quality=95)
        expected = os.path.join(settings.MEDIA_ROOT, basename)
        expected += '_240x120_crop_q95.jpg'
        self.verify_thumbnail((240, 120), thumb, expected_filename=expected)

        # All options on
        thumb = DjangoThumbnail(relative_source=RELATIVE_PIC_NAME,
                                requested_size=(240, 120), opts=VALID_OPTIONS)
        expected = os.path.join(settings.MEDIA_ROOT, basename)
        expected += '_240x120_bw_autocrop_crop_upscale_detail_sharpen_q85.jpg'
        self.verify_thumbnail((240, 120), thumb, expected_filename=expected)

        # Different basedir
        basedir = 'sorl-thumbnail-test-basedir'
        self.change_settings.change({'BASEDIR': basedir})
        thumb = DjangoThumbnail(relative_source=self.pic_subdir,
                                requested_size=(240, 120))
        expected = os.path.join(basedir, self.sub_dir, basename)
        expected += '_240x120_q85.jpg'
        self.verify_thumbnail((160, 120), thumb, expected_filename=expected)
        # Different subdir
        self.change_settings.change({'BASEDIR': '', 'SUBDIR': 'subdir'})
        thumb = DjangoThumbnail(relative_source=self.pic_subdir,
                                requested_size=(240, 120))
        expected = os.path.join(settings.MEDIA_ROOT,
                                os.path.basename(self.sub_dir), 'subdir',
                                basename)
        expected += '_240x120_q85.jpg'
        self.verify_thumbnail((160, 120), thumb, expected_filename=expected)
        # Different prefix
        self.change_settings.change({'SUBDIR': '', 'PREFIX': 'prefix-'})
        thumb = DjangoThumbnail(relative_source=self.pic_subdir,
                                requested_size=(240, 120))
        expected = os.path.join(self.sub_dir, 'prefix-'+basename)
        expected += '_240x120_q85.jpg'
        self.verify_thumbnail((160, 120), thumb, expected_filename=expected)

    def testAlternateExtension(self):
        basename = RELATIVE_PIC_NAME.replace('.', '_')
        # Control JPG
        thumb = DjangoThumbnail(relative_source=RELATIVE_PIC_NAME,
                                requested_size=(240, 120))
        expected = os.path.join(settings.MEDIA_ROOT, basename)
        expected += '_240x120_q85.jpg'
        expected_jpg = expected
        self.verify_thumbnail((160, 120), thumb, expected_filename=expected)
        # Test PNG
        thumb = DjangoThumbnail(relative_source=RELATIVE_PIC_NAME,
                                requested_size=(240, 120), extension='png')
        expected = os.path.join(settings.MEDIA_ROOT, basename)
        expected += '_240x120_q85.png'
        self.verify_thumbnail((160, 120), thumb, expected_filename=expected)
        # Compare the file size to make sure it's not just saving as a JPG with
        # a different extension.
        self.assertNotEqual(os.path.getsize(expected_jpg),
                            os.path.getsize(expected))

    def tearDown(self):
        super(DjangoThumbnailTest, self).tearDown()
        subdir = os.path.join(self.sub_dir, 'subdir')
        if os.path.exists(subdir):
            os.rmdir(subdir)
        os.rmdir(self.sub_dir)
