Settings
========

``THUMBNAIL_DEBUG``
-------------------

- Default: ``False``

When set to ``True`` the ``ThumbnailNode.render`` method can raise errors.
Django recommends that tags never raise errors in the ``Node.render`` method
but since sorl-thumbnail is such a complex tag we will need to have more
debuging available, this this setting.


``THUMBNAIL_BACKEND``
---------------------

- Default: ``'sorl.thumbnail.base.ThumbnailBackend'``

This is the entrypoint for generating thumbnails, you probably want to keep the
default one but just in case you would like to generate thumbnails filenames
differently or need som special functionality you can override this and use
your own implementation.


``THUMBNAIL_KVSTORE``
---------------------

- Default: ``'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'``

sorl-thumbnail needs a Key Value Store to :doc:`/operation`.
sorl-thumbnail ships with suport for two Key Value Stores:

Redis
~~~~~
``sorl.thumbnail.kvstores.redis_kvstore.KVStore``. This is the preferred Key
Value Store because it is the fastest. It is not default because it requires
you to install a redis server as well as a `redis python client
<https://github.com/andymccurdy/redis-py/>`_

Cached DB
~~~~~~~~~
``sorl.thumbnail.kvstores.cached_db_kvstore.KVStore``. This is the default
Key Value Store because it does not require any special installation.


``THUMBNAIL_ENGINE``
--------------------

= Default: ``'sorl.thumbnail.engines.pil_engine.Engine'``

This is the processing class for sorl-thumbnail. It does all the
resizing, cropping or whatever processing you want to perform.
sorl-thumbnail ships with two engines:

Pgmagick
~~~~~~~~
``'sorl.thumbnail.engines.pgmagick_engine.Engine'`` This is the preferrred
engine because it produces the best quality and it can handle CMYK sources.
Pgmagick uses `Graphics <http://www.graphicsmagick.org/>`_ which is much more
competent library than PIL.

PIL
~~~
``'sorl.thumbnail.engines.pil_engine.Engine'``. This is the default option
because it is what most people have instaled already.


``THUMBNAIL_STORAGE``
---------------------

- Defualt: ``settings.DEFAULT_FILE_STORAGE``

The storage class to use for the generated thumbnails.


``THUMBNAIL_REDIS_HOST``
------------------------

- Default: ``'localhost'``

The host for Redis server. Only applicable for the Redis Key Value Store


``THUMBNAIL_REDIS_PORT``
------------------------

- Default: ``6379``

The port for Redis server. Only applicable for the Redis Key Value Store


``THUMBNAIL_REDIS_DB``
----------------------

- Default: ``0``

The redis database. Only applicable for the Redis Key Value Store


``THUMBNAIL_CACHE_TIMEOUT``
- Default: ``sys.maxint``

Cache timeout for Cached DB Key Value Store. You should probably keep this at
maximum or ``None`` if your caching backend can handle that as infinate.
Only applicable for the Cached DB Key Value Store.


``THUMBNAIL_KEY_PREFIX``
------------------------

- Default: ``'sorl-thumbnail'``

Key prefix used by the key value store.


``THUMBNAIL_PREFIX``
--------------------

- Default: ``'cache/'``

The generated thumbnails filename prefix.


``THUMBNAIL_FORMAT``
--------------------

- Default: ``'JPEG'``

Default image format, supported formats are: ``'JPEG'``, ``'PNG'``. This also implicitly
sets the filename extension. This can be overridden by individual options.


``THUMBNAIL_COLORSPACE``
------------------------

- Default: ``'RGB'``

Default thumbnail colorspace, engines are required to implement: ``'RGB'``,
``'GRAY'`` Setting this to None will keep the original colorspace. This can be
overridden by individual options.


``THUMBNAIL_UPSCALE``
---------------------

- Default: ``True``

Should we upscale by default? ``True`` means we upscale images by default.
``False`` means we don't. This can be overridden by individual options.


``THUMBNAIL_QUALITY``
---------------------

- Default: ``95``

Default thumbnail quality. A value between 0 and 100 is allowed. This can be
overridden by individual options.



``THUMBNAIL_ERROR``
-------------------

- Default: ``''``

This is what will populate the context variable when an error is raised and
``THUMBNAIL_DEBUG`` is set to ``False``.



``THUMBNAIL_DUMMY``
-------------------

- Default: ``False``

This is a very powerful option which came from real world frustration. The use
case is when you want to do development on a deployed project that has image
references in its database. Instead of downloading all the image files from the
server hosting the deployed project and all its thumbnails we just set this
option to ``True``. This will generate placeholder images for all thumbnails
regardless of the input source.


``THUMBNAIL_DUMMY_RATIO``
-------------------------

Default: ``3.0 / 2``

This option is only applicable if ``THUMBNAIL_DUMMY`` is set to true. This
value sets an image ratio to all thumbnails that are not defined by width
**and** height since we cannot determine from the file input (since we don't
have that).

