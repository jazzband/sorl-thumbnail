|travis| |pypi|

Thumbnails for Django.

Features at a glance
====================

- Storage support
- Pluggable Engine support for `Pillow`_, `ImageMagick`_, `PIL`_, `Wand`_ and `pgmagick`_
- Pluggable Key Value Store support (cached db, redis)
- Pluggable Backend support
- Admin integration with possibility to delete
- Dummy generation (placeholders)
- Flexible, simple syntax, generates no html
- ImageField for model that deletes thumbnails
- CSS style cropping options
- Back smart cropping, and remove borders from the images when cropping
- Margin calculation for vertical positioning
- Alternative resolutions versions of a thumbnail

Read more in `the documentation (latest version) <http://sorl-thumbnail.rtfd.org/>`_

How to Use
==========

Get the code
------------

Getting the code for the latest stable release use 'pip'. ::

   $ pip install sorl-thumbnail

Install in your project
-----------------------

Then register 'sorl.thumbnail', in the 'INSTALLED_APPS' section of
your project's settings. ::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.sites',
        'django.contrib.comments',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.contenttypes',

        'sorl.thumbnail',
    )


Templates Usage
----------------

All of the examples assume that you first load the thumbnail template tag in
your template.::

    {% load thumbnail %}


A simple usage. ::

    {% thumbnail item.image "100x100" crop="center" as im %}
        <img src="{{ im.url }}" width="{{ im.width }}" height="{{ im.height }}">
    {% endthumbnail %}

See more examples in the section `Template examples`_ in the Documentation

Model Usage
-----------

Using the ImageField that automatically deletes references to itself in the key
value store and its thumbnail references and the thumbnail files when deleted.::

    from django.db import models
    from sorl.thumbnail import ImageField

    class Item(models.Model):
        image = ImageField(upload_to='whatever')

See more examples in the section `Model examples`_ in the Documentation

Low level API
-------------

You can use the 'get_thumbnail'::

    from sorl.thumbnail import get_thumbnail
    from sorl.thumbnail import delete

    im = get_thumbnail(my_file, '100x100', crop='center', quality=99)
    delete(my_file)

See more examples in the section `Low level API examples`_ in the Documentation



.. |travis| image:: https://secure.travis-ci.org/mariocesar/sorl-thumbnail.png?branch=master
    :target: https://travis-ci.org/mariocesar/sorl-thumbnail
.. |pypi| image:: https://badge.fury.io/py/sorl-thumbnail.png
    :target: http://badge.fury.io/py/sorl-thumbnail

.. _`Pillow`: http://pillow.readthedocs.org/en/latest/
.. _`ImageMagick`: http://www.imagemagick.org/script/index.php
.. _`PIL`: http://www.pythonware.com/products/pil/
.. _`Wand`: http://docs.wand-py.org/
.. _`pgmagick`: http://pgmagick.readthedocs.org/en/latest/

.. _`Template examples`: http://sorl-thumbnail.readthedocs.org/en/latest/examples.html#template-examples
.. _`Model examples`: http://sorl-thumbnail.readthedocs.org/en/latest/examples.html#model-examples
.. _`Low level API examples`: http://sorl-thumbnail.readthedocs.org/en/latest/examples.html#low-level-api-examples
