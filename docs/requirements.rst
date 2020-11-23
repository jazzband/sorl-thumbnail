************
Requirements
************
 
Base requirements
=================
- `Python`_ 3.6+
- `Django`_
- :ref:`kvstore-requirements`
- :ref:`image-library`

.. _kvstore-requirements:

Key Value Store
===============
sorl-thumbnail needs a Key Value Store for its operation. You can choose between
a **cached database** which requires no special installation to your normal
Django setup besides installing a proper cache like memcached **or** you can
setup **redis** which requires a little bit more work.

Cached DB
---------
All you need to use the cached database key value store is a database and `cache
<http://docs.djangoproject.com/en/dev/topics/cache/>`_ setup properly using
memcached. This cache needs to be really fast so **using anything else than
memcached is not recomended**.

Redis
-----
Redis is a fast key value store also suited for the job. To use the `redis`_ key
value store you first need to install the `redis server
<http://code.google.com/p/redis/>`_.  After that install the `redis client
<https://github.com/andymccurdy/redis-py/>`_::

    pip install redis


.. _image-library:

Image Library
=============
You need to have an image library installed. sorl-thumbnail ships with support
for `Python Imaging Library`_, `pgmagick`_, `ImageMagick`_ (or `GraphicsMagick`)
command line tools. `pgmagick`_ are python bindings for `GraphicsMagick`_
(Magick++)`,

The `ImageMagick`_ based engine ``sorl.thumbnail.engines.convert_engine.Engine``
by default calls ``convert`` and ``identify`` shell commands. You can change the
paths to these tools by setting ``THUMBNAIL_CONVERT`` and ``THUMBNAIL_IDENTIFY``
respectively.  Note that you need to change these to use `GraphicsMagick`_ to
``/path/to/gm convert`` and ``/path/to/gm identify``.

Python Imaging Library installation
-----------------------------------
Prerequisites:

- libjpeg
- zlib

Ubuntu 10.04 package installation::

    sudo apt-get install libjpeg62 libjpeg62-dev zlib1g-dev

Installing `Python Imaging Library`_ using pip::

    pip install Pillow

Watch the output for messages on what support got compiled in, you at least
want to see the following::

    --- JPEG support available
    --- ZLIB (PNG/ZIP) support available

pgmagick installation
---------------------
Prerequisites:

- GraphicsMagick
- Boost.Python

Ubuntu 10.04 package installation::

    sudo apt-get install libgraphicsmagick++-dev
    sudo apt-get install libboost-python1.40-dev

Fedora installation::

    yum install GraphicsMagick-c++-devel
    yum install boost-devel

Installing `pgmagick`_ using pip::

    pip install pgmagick

ImageMagick installation
------------------------
Ubuntu 10.04 package installation::

    sudo apt-get install imagemagick

Or if you prefer `GraphicsMagick`_::

    sudo apt-get install graphicsmagick

Wand installation
------------------------

Ubuntu installation::

    apt-get install libmagickwand-dev
    pip install Wand


.. _Python Imaging Library: http://www.pythonware.com/products/pil/
.. _ImageMagick: http://imagemagick.com/
.. _GraphicsMagick: http://www.graphicsmagick.org/
.. _redis: http://code.google.com/p/redis/
.. _redis-py: https://github.com/andymccurdy/redis-py/
.. _Django: http://www.djangoproject.com/
.. _Python: http://www.python.org/
.. _pgmagick: http://bitbucket.org/hhatto/pgmagick/src
.. _wand: http://wand-py.org
