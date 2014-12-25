# -*- coding: utf-8 -*-
import os

import pytest
from django.utils.six import StringIO
from django.core import management

from sorl.thumbnail.conf import settings
from .models import Item
from .utils import BaseTestCase


pytestmark = pytest.mark.django_db


class CommandTests(BaseTestCase):
    def make_test_thumbnails(self, *sizes):
        item = Item.objects.get(image='500x500.jpg')
        names = []
        for size in sizes:
            th = self.BACKEND.get_thumbnail(item.image, size)
            name = os.path.join(settings.MEDIA_ROOT, th.name)
            self.assertTrue(os.path.isfile(name))
            names.append(name)
        return names

    def test_clear_action(self):
        """ Only the KV store is cleared. """
        name1, name2 = self.make_test_thumbnails('400x300', '200x200')
        out = StringIO('')
        management.call_command('thumbnail', 'clear', verbosity=1, stdout=out)
        self.assertEqual(out.getvalue(), "Clear the Key Value Store ... [Done]\n")
        self.assertTrue(os.path.isfile(name1))
        self.assertTrue(os.path.isfile(name2))

    def test_clear_delete_referenced_action(self):
        """ Clear KV store and delete referenced thumbnails """
        name1, name2 = self.make_test_thumbnails('400x300', '200x200')
        management.call_command('thumbnail', 'clear', verbosity=0)
        name3, = self.make_test_thumbnails('100x100')
        out = StringIO('')
        management.call_command('thumbnail', 'clear_delete_referenced', verbosity=1, stdout=out)
        lines = out.getvalue().split("\n")
        self.assertEqual(lines[0], "Delete all thumbnail files referenced in Key Value Store ... [Done]")
        self.assertEqual(lines[1], "Clear the Key Value Store ... [Done]")
        self.assertTrue(os.path.isfile(name1))
        self.assertTrue(os.path.isfile(name2))
        self.assertFalse(os.path.isfile(name3))

    def test_clear_delete_all_action(self):
        """ Clear KV store and delete all thumbnails """
        name1, name2 = self.make_test_thumbnails('400x300', '200x200')
        management.call_command('thumbnail', 'clear', verbosity=0)
        name3, = self.make_test_thumbnails('100x100')
        out = StringIO('')
        management.call_command('thumbnail', 'clear_delete_all', verbosity=1, stdout=out)
        lines = out.getvalue().split("\n")
        self.assertEqual(lines[0], "Clear the Key Value Store ... [Done]")
        self.assertEqual(lines[1], "Delete all thumbnail files in THUMBNAIL_PREFIX ... [Done]")
        self.assertFalse(os.path.isfile(name1))
        self.assertFalse(os.path.isfile(name2))
        self.assertFalse(os.path.isfile(name3))

    def test_cleanup_action(self):
        out = StringIO('')
        management.call_command('thumbnail', 'cleanup', verbosity=1, stdout=out)
        self.assertEqual(out.getvalue(), "Cleanup thumbnails ... [Done]\n")

