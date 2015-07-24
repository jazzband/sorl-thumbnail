# coding: utf-8
from __future__ import unicode_literals
import os
import shutil
import unittest
import logging
from contextlib import contextmanager
from subprocess import check_output

from PIL import Image, ImageDraw
from django.test.signals import setting_changed
from django.conf import UserSettingsHolder

from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.log import ThumbnailLogHandler
from .models import Item
from .storage import MockLoggingHandler

DATA_DIR = os.path.join(settings.MEDIA_ROOT, 'data')

handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)


@contextmanager
def same_open_fd_count(testcase):
    num_opened_fd_before = get_open_fds_count()
    yield
    num_opened_fd_after = get_open_fds_count()
    testcase.assertEqual(
        num_opened_fd_before, num_opened_fd_after,
        'Open descriptors count changed, was %s, now %s' % (num_opened_fd_before,
                                                            num_opened_fd_after)
    )


def get_open_fds_count():
    """Return the number of open file descriptors for current process

        .. warning: will only work on UNIX-like os-es.
    """
    pid = os.getpid()
    procs = check_output(["lsof", '-w', '-Ff', "-p", str(pid)])
    nprocs = len(
        [s for s in procs.decode('utf-8').split('\n') if s and s[0] == 'f' and s[1:].isdigit()]
    )
    return nprocs


class override_custom_settings(object):
    """
    settings overrider context manager.
    https://github.com/django/django/blob/1.6.2/django/test/utils.py#L209-L268
    """

    def __init__(self, settings_obj, **kwargs):
        self.settings = settings_obj
        self.options = kwargs

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def enable(self):
        override = UserSettingsHolder(self.settings._wrapped)
        for key, new_value in self.options.items():
            setattr(override, key, new_value)
        self.wrapped = self.settings._wrapped
        self.settings._wrapped = override
        for key, new_value in self.options.items():
            setting_changed.send(sender=self.settings._wrapped.__class__,
                                 setting=key, value=new_value, enter=True)

    def disable(self):
        self.settings._wrapped = self.wrapped
        del self.wrapped
        for key in self.options:
            new_value = getattr(self.settings, key, None)
            setting_changed.send(sender=self.settings._wrapped.__class__,
                                 setting=key, value=new_value, enter=False)


class FakeFile(object):
    """
    Used to test the _get_format method.
    """

    def __init__(self, name):
        self.name = name


class BaseTestCase(unittest.TestCase):
    IMAGE_DIMENSIONS = [(500, 500), (100, 100), (200, 100), ]
    BACKEND = None
    ENGINE = None
    KVSTORE = None

    def create_image(self, name, dim, transparent=False):
        """
        Creates an image and prepends the MEDIA ROOT path.
        :param name: e.g. 500x500.jpg
        :param dim: a dimension tuple e.g. (500, 500)
        """
        filename = os.path.join(settings.MEDIA_ROOT, name)
        im = Image.new('L', dim)

        if transparent:
            draw = ImageDraw.Draw(im)
            draw.line((0, 0) + im.size, fill=128)
            draw.line((0, im.size[1], im.size[0], 0), fill=128)

            im.save(filename, transparency=0)
        else:
            im.save(filename)

        return Item.objects.get_or_create(image=name)

    def is_transparent(self, img):
        return img.mode in ('RGBA', 'LA') or 'transparency' in img.info

    def setUp(self):
        self.BACKEND = get_module_class(settings.THUMBNAIL_BACKEND)()
        self.ENGINE = get_module_class(settings.THUMBNAIL_ENGINE)()
        self.KVSTORE = get_module_class(settings.THUMBNAIL_KVSTORE)()

        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
            shutil.copytree(settings.DATA_ROOT, DATA_DIR)

        for dimension in self.IMAGE_DIMENSIONS:
            name = '%sx%s.jpg' % dimension
            self.create_image(name, dimension)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)


class BaseStorageTestCase(unittest.TestCase):
    image = None
    name = None

    def setUp(self):
        os.makedirs(settings.MEDIA_ROOT)
        filename = os.path.join(settings.MEDIA_ROOT, self.name)
        Image.new('L', (100, 100)).save(filename)
        self.image = ImageFile(self.name)

        logger = logging.getLogger('slog')
        logger.setLevel(logging.DEBUG)
        handler = MockLoggingHandler(level=logging.DEBUG)
        logger.addHandler(handler)
        self.log = handler.messages['debug']

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
