from django.core.files.storage import FileSystemStorage


class SlogHandler(object):
    _log = []
    _active = False

    def start_log(self):
        self._active = True

    def stop_log(self):
        self._active = False
        log = self._log[:]
        self._log = []
        return log

    def log(self, s):
        if self._active:
            self._log.append(s)


slog = SlogHandler()


class TestStorageMixin(object):
    def open(self, name, *args, **kwargs):
        slog.log('open: %s' % name)
        return super(TestStorageMixin, self).open(name, *args, **kwargs)

    def save(self, name, *args, **kwargs):
        slog.log('save: %s' % name)
        return super(TestStorageMixin, self).save(name, *args, **kwargs)

    def get_valid_name(self, name, *args, **kwargs):
        slog.log('get_valid_name: %s' % name)
        return super(TestStorageMixin, self).get_valid_name(name, *args, **kwargs)

    def get_available_name(self, name, *args, **kwargs):
        slog.log('get_available_name: %s' % name)
        return super(TestStorageMixin, self).get_available_name(name, *args, **kwargs)

    def path(self, name, *args, **kwargs):
        #slog.log('path: %s' % name)
        return super(TestStorageMixin, self).path(name, *args, **kwargs)

    def delete(self, name, *args, **kwargs):
        slog.log('delete: %s' % name)
        return super(TestStorageMixin, self).delete(name, *args, **kwargs)

    def exists(self, name, *args, **kwargs):
        slog.log('exists: %s' % name)
        return super(TestStorageMixin, self).exists(name, *args, **kwargs)

    def listdir(self, name, *args, **kwargs):
        slog.log('listdir: %s' % name)
        return super(TestStorageMixin, self).listdir(name, *args, **kwargs)

    def size(self, name, *args, **kwargs):
        slog.log('size: %s' % name)
        return super(TestStorageMixin, self).size(name, *args, **kwargs)

    def url(self, name, *args, **kwargs):
        #slog.log('url: %s' % name)
        return super(TestStorageMixin, self).url(name, *args, **kwargs)

    def accessed_time(self, name, *args, **kwargs):
        slog.log('accessed_time: %s' % name)
        return super(TestStorageMixin, self).accessed_time(name, *args, **kwargs)

    def created_time(self, name, *args, **kwargs):
        slog.log('created_time: %s' % name)
        return super(TestStorageMixin, self).created_time(name, *args, **kwargs)

    def modified_time(self, name, *args, **kwargs):
        slog.log('modified_time: %s' % name)
        return super(TestStorageMixin, self).modified_time(name, *args, **kwargs)


class TestStorage(TestStorageMixin, FileSystemStorage):
    pass

