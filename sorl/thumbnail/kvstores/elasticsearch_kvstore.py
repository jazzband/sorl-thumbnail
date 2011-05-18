from pyes import ES
from pyes.query import Search, PrefixQuery

from sorl.thumbnail.kvstores.base import KVStoreBase
from sorl.thumbnail.conf import settings

def setup_store():
    connection = ES(settings.THUMBNAIL_ELASTIC_SEARCH_SERVERS)
    try:
        connection.create_index_if_missing(settings.THUMBNAIL_ELASTIC_SEARCH_INDEX)
    except:
        pass
    try:
        connection.put_mapping(settings.THUMBNAIL_ELASTIC_SEARCH_DOCUMENT_TYPE,
                               settings.THUMBNAIL_ELASTIC_SEARCH_MAPPING,
                               indexes=[settings.THUMBNAIL_ELASTIC_SEARCH_INDEX,])
    except:
        pass

class KVStore(KVStoreBase):
    def __init__(self, *args, **kwargs):
        super(KVStore, self).__init__(*args, **kwargs)
        self.connection = ES(settings.THUMBNAIL_ELASTIC_SEARCH_SERVERS)

    def _get_raw(self, key):
        try:
            #import pdb; pdb.set_trace()
            value = self.connection.get(settings.THUMBNAIL_ELASTIC_SEARCH_INDEX, 
                                        settings.THUMBNAIL_ELASTIC_SEARCH_DOCUMENT_TYPE,
                                        key)
            return value['_source']['value']
        except:
            return None

    def _set_raw(self, key, value):
        ret = self.connection.index({"value": value}, 
                                    settings.THUMBNAIL_ELASTIC_SEARCH_INDEX,
                                    settings.THUMBNAIL_ELASTIC_SEARCH_DOCUMENT_TYPE,
                                    key)
        return ret['ok']
    
    def _delete_raw(self, *keys):
        rets = []
        for key in keys:
            try:
                ret = self.connection.delete(settings.THUMBNAIL_ELASTIC_SEARCH_INDEX,
                                             settings.THUMBNAIL_ELASTIC_SEARCH_DOCUMENT_TYPE,
                                             key)
                rets.append(ret['ok'])
            except:
                rets.append(False)
        return rets

    def _find_keys_raw(self, prefix):
        search = Search(query=PrefixQuery("_id", prefix), size=1000, start=0, fields=[])
        results = self.connection.search(search, 
                                         indexes=[settings.THUMBNAIL_ELASTIC_SEARCH_INDEX,], 
                                         doc_types=[settings.THUMBNAIL_ELASTIC_SEARCH_DOCUMENT_TYPE,])
        return [hit['_id'] for hit in results['hits']['hits']]


      