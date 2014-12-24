from __future__ import unicode_literals
import logging

from django.core.files.storage import FileSystemStorage


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        super(MockLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {'debug': [], 'info': [], 'warning': [], 'error': [], 'critical': []}


slog = logging.getLogger('slog')


class TestStorageMixin(object):
    def open(self, name, *args, **kwargs):
        slog.debug('open: %s' % name)
        return super(TestStorageMixin, self).open(name, *args, **kwargs)

    def save(self, name, *args, **kwargs):
        slog.debug('save: %s' % name)
        return super(TestStorageMixin, self).save(name, *args, **kwargs)

    def get_valid_name(self, name, *args, **kwargs):
        slog.debug('get_valid_name: %s' % name)
        return super(TestStorageMixin, self).get_valid_name(name, *args, **kwargs)

    def get_available_name(self, name, *args, **kwargs):
        slog.debug('get_available_name: %s' % name)
        return super(TestStorageMixin, self).get_available_name(name, *args, **kwargs)

    def path(self, name, *args, **kwargs):
        # slog.debug('path: %s' % name)
        return super(TestStorageMixin, self).path(name, *args, **kwargs)

    def delete(self, name, *args, **kwargs):
        slog.debug('delete: %s' % name)
        return super(TestStorageMixin, self).delete(name, *args, **kwargs)

    def exists(self, name, *args, **kwargs):
        slog.debug('exists: %s' % name)
        return super(TestStorageMixin, self).exists(name, *args, **kwargs)

    def listdir(self, name, *args, **kwargs):
        slog.debug('listdir: %s' % name)
        return super(TestStorageMixin, self).listdir(name, *args, **kwargs)

    def size(self, name, *args, **kwargs):
        slog.debug('size: %s' % name)
        return super(TestStorageMixin, self).size(name, *args, **kwargs)

    def url(self, name, *args, **kwargs):
        # slog.debug('url: %s' % name)
        return super(TestStorageMixin, self).url(name, *args, **kwargs)

    def accessed_time(self, name, *args, **kwargs):
        slog.debug('accessed_time: %s' % name)
        return super(TestStorageMixin, self).accessed_time(name, *args, **kwargs)

    def created_time(self, name, *args, **kwargs):
        slog.debug('created_time: %s' % name)
        return super(TestStorageMixin, self).created_time(name, *args, **kwargs)

    def modified_time(self, name, *args, **kwargs):
        slog.debug('modified_time: %s' % name)
        return super(TestStorageMixin, self).modified_time(name, *args, **kwargs)


class TestStorage(TestStorageMixin, FileSystemStorage):
    pass
