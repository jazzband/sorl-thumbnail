from abc import ABCMeta, abstractmethod
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import serialize, deserialize
from sorl.thumbnail.storage import ImageFile
from sorl.thumbnail.storage import serialize_image_file, deserialize_image_file


def add_prefix(key, identity='image'):
    """
    Adds prefixes to the key
    """
    return '||'.join([settings.THUMBNAIL_KEY_PREFIX, identity, key])


class KVStoreBase(object):
    __metaclass__ = ABCMeta

    def get(self, image_file):
        """
        Gets the ``image_file`` from store. Returns ``None`` if not found.
        """
        return self._get(image_file.key)

    def set(self, image_file, source=None):
        """
        Updates store for the `image_file`. Makes sure the `image_file` has a
        size set.
        """
        if source is not None:
            # Update the list of thumbnails for source. Storage is not saved,
            # we assume current storage when unpacking.
            thumbnails = self._get(source.key, identity='thumbnails') or []
            thumbnails = set(thumbnails)
            thumbnails.add(image_file.name)
            self._set(source.key, list(thumbnails), identity='thumbnails')
        image_file.set_size() # make sure its got a size
        self._set(image_file.key, image_file)

    def delete(self, image_file, delete_thumbnails=True):
        """
        Deletes the referense to the ``image_file`` and deletes the references
        to thumbnails as well as thumbnail files if ``delete_thumbnails`` is
        `True``. Does not delete the ``image_file`` is self.
        """
        if delete_thumbnails:
            self.delete_thumbnails(image_file)
        self._delete(image_file.key)

    def delete_thumbnails(self, image_file, storage=None):
        """
        Deletes references to thumbnails as well as thumbnail ``image_files``.
        """
        if storage is not None:
            storage = self.storage
        thumbnails = self._get(image_file.key, identity='thumbnails')
        if thumbnails:
            # Delete all thumbnail keys from store and delete the
            # ImageFiles. Storage is assumed to be the same
            for name in thumbnails:
                thumbnail = ImageFile(name, storage)
                self._delete(thumbnail.key)
                thumbnail.delete()
        # Delete the thumbnails key from store
        self._delete(image_file.key, identity='thumbnails')

    def _get(self, key, identity='image'):
        """
        Deserializing, prefix wrapper for _get_raw
        """
        value = self._get_raw(add_prefix(key, identity))
        if value is None:
            return None
        if identity == 'image':
            return deserialize_image_file(value)
        return deserialize(value)

    def _set(self, key, value, identity='image'):
        """
        Serializing, prefix wrapper for _set_raw
        """
        if identity == 'image':
            s = serialize_image_file(value)
        else:
            s = serialize(value)
        self._set_raw(add_prefix(key, identity), s)

    def _delete(self, key, identity='image'):
        """
        Prefix wrapper for _delete_raw
        """
        self._delete_raw(add_prefix(key, identity))

    def _delete_orphans(self):
        """
        Deletes all store key references for image_files that do not exist.
        Also deletes all key references for thumbnails *and* their
        image_files. This can be used in *emergency* situations.
        """
        keys = self._find_keys(identity='image')
        for key in keys:
            value = self._get_raw(key)
            image_file = deserialize_image_file(value)
            if not image_file.exists():
                self.delete(image_file)

    #
    # Methods which key-value stores need to implement
    #
    @abstractmethod
    def _get_raw(self, key):
        """
        Gets the value from keystore, returns `None` if not found.
        """
        raise NotImplemented()

    @abstractmethod
    def _set_raw(self, key, value):
        """
        Sets value associated to key. Key is expected to be shorter than 200
        chars. Value is a ``unicode`` object with an unknown (reasonable)
        length.
        """
        raise NotImplemented()

    @abstractmethod
    def _delete_raw(self, key):
        """
        Deletes the key, value. Silent failure for missing key.
        """
        raise NotImplemented()

    @abstractmethod
    def _find_keys(self, identity):
        """
        Finds and returns all keys for identity
        """
        raise NotImplemented()

