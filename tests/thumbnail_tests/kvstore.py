from sorl.thumbnail.kvstores.cached_db_kvstore import KVStore


class KVlogHandler(object):
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


kvlog = KVlogHandler()


class TestKvStoreMixin(object):
    def get(self, *args, **kwargs):
        kvlog.log('get')
        return super(TestKvStoreMixin, self).get(*args, **kwargs)

    def set(self, *args, **kwargs):
        kvlog.log('set')
        return super(TestKvStoreMixin, self).set(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kvlog.log('delete')
        return super(TestKvStoreMixin, self).delete(*args, **kwargs)


class TestKVStore(TestKvStoreMixin, KVStore):
    pass

