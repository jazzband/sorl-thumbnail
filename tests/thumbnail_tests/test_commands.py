from datetime import datetime
from io import StringIO
from unittest import mock
import os

import pytest
from django.core import management
from django.core.management.base import CommandError

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
        self.assertEqual(lines[0],
                         "Delete all thumbnail files referenced in Key Value Store ... [Done]")
        self.assertEqual(lines[1], "Clear the Key Value Store ... [Done]")
        self.assertTrue(os.path.isfile(name1))
        self.assertTrue(os.path.isfile(name2))
        self.assertFalse(os.path.isfile(name3))

    def _test_clear_delete_referenced_timeout(self, timeout):
        """
        Clear KV store and delete referenced thumbnails for thumbnails older
        than the specified timeout.
        """
        name1, name2 = self.make_test_thumbnails('400x300', '200x200')
        out = StringIO()
        with mock.patch('tests.thumbnail_tests.storage.TestStorage.get_created_time') as mocked:
            mocked.return_value = datetime(2016, 9, 29, 12, 58, 27)
            management.call_command(
                'thumbnail', 'clear_delete_referenced', f'--timeout={timeout}',
                verbosity=1, stdout=out
            )
        lines = out.getvalue().split("\n")
        self.assertRegex(
            lines[0],
            "Delete all thumbnail files referenced in Key Value Store "
            r"older than \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \.\.\. \[Done\]"
        )
        self.assertFalse(os.path.isfile(name1))
        self.assertFalse(os.path.isfile(name2))

    def test_clear_delete_referenced_timeout_digits(self):
        self._test_clear_delete_referenced_timeout('7776000')

    def test_clear_delete_referenced_timeout_duration(self):
        self._test_clear_delete_referenced_timeout('P180D')

    def test_clear_delete_referenced_timeout_invalid(self):
        with self.assertRaisesMessage(CommandError, "Unable to parse 'XX360' as a duration"):
            self._test_clear_delete_referenced_timeout('XX360')

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
