from __future__ import unicode_literals

from boto.dynamodb2.table import Table
import boto
import json
from sorl.thumbnail.kvstores.base import KVStoreBase
from sorl.thumbnail.conf import settings


class KVStore(KVStoreBase):
    def __init__(self):
        super(KVStore, self).__init__()
        conn = boto.dynamodb2.connect_to_region(settings.AWS_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        self.table = Table(settings.THUMBNAIL_DYNAMODB_NAME, connection=conn)

    def _get_raw(self, key):
        try:
            return self.table.get_item(key=key)['value']
        except boto.dynamodb2.exceptions.ItemNotFound:
            pass

    def _set_raw(self, key, value):
        try:
            item = self.table.get_item(key=key)
        except boto.dynamodb2.exceptions.ItemNotFound:
            item = self.table.new_item()
            item['key'] = key
        item['value'] = value
        item.save(overwrite=True)

    def _delete_raw(self, *keys):
        [self.table.delete_item(key=k) for k in keys]

    def _find_keys_raw(self, prefix):
        return [i['key'] for i in self.table.scan(key__beginswith=prefix)]
