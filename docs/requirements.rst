Requirements
============

Base requirements
-----------------
- `Python`_ 2.6+
- `Django`_
- :ref:`kvstore-requirements`
- :ref:`image-library`
  
.. _kvstore-requirements:

Key Value Store
---------------
Support for `redis`_ and a cached database key value store is shipped with
sorl-thumbnail. `redis`_ is the best option. To use the `redis`_ key value store
you need to install `redis-py`_::

    pip install redis

To use the cached database key value store you need to have a `database defined
<http://docs.djangoproject.com/en/dev/ref/settings/?from=olddocs#databases>`_ in
your `Django`_ settings and preferably cache setup properly.

.. _image-library:

Image Library
-------------
You need to have an image library installed. sorl-thumbnail ships with support
for `Python Imaging Library`_ and `pgmagick`_. `pgmagick`_ are python bindings
for GraphicsMagick (Magick++) and is the preferred option.

pgmagick installation
^^^^^^^^^^^^^^^^^^^^^^
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

Python Imaging Library installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Prerequisites:

- libjpeg
- zlib

Ubuntu 10.04 package installation::

    sudo aptitude install libjpeg62 libjpeg62-dev zlib1g-dev

Installing `Python Imaging Library`_ using pip::

    pip install PIL

Watch the output for messages on what support got compiled in, you at least
want to see the following::

    --- JPEG support available
    --- ZLIB (PNG/ZIP) support available


.. _Python Imaging Library: http://www.pythonware.com/products/pil/
.. _redis: http://code.google.com/p/redis/
.. _redis-py: https://github.com/andymccurdy/redis-py/
.. _Django: http://www.djangoproject.com/
.. _Python: http://www.python.org/
.. _pgmagick: http://bitbucket.org/hhatto/pgmagick/src

