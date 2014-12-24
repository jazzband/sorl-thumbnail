# coding: utf-8
from __future__ import unicode_literals
import os
from contextlib import contextmanager
from subprocess import check_output

from django.test.signals import setting_changed
from django.conf import UserSettingsHolder


@contextmanager
def same_open_fd_count(testcase):
    num_opened_fd_before = get_open_fds_count()
    yield
    num_opened_fd_after = get_open_fds_count()
    testcase.assertEqual(
        num_opened_fd_before, num_opened_fd_after,
        'Open descriptors count changed, was %s, now %s' % (num_opened_fd_before, num_opened_fd_after)
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
