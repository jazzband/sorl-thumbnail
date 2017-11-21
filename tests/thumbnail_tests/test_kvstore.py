# -*- coding: utf-8 -*-
import threading
import unittest

from sorl.thumbnail.kvstores.cached_db_kvstore import KVStore


class KVStoreTestCase(unittest.TestCase):
    @unittest.skipIf(threading is None, 'Test requires threading')
    def test_cache_backend(self):
        kv = KVStore()
        cache_backends = []

        def thread_cache_backend():
            cache_backends.append(kv.cache)

        for _ in range(2):
            t = threading.Thread(target=thread_cache_backend)
            t.start()
            t.join()

        # Cache backend for each thread needs to be unique
        self.assertNotEqual(cache_backends[0], cache_backends[1])
