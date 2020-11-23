|jazzband-badge| |pypi| |docs| |gh-actions| |codecov|

Thumbnails for Django.

Features at a glance
====================

- Support for Django 2.2, 3.0 and 3.1 following the `Django supported versions policy`_
- Python 3 support
- Storage support
- Pluggable Engine support for `Pillow`_, `ImageMagick`_, `PIL`_, `Wand`_, `pgmagick`_, and `vipsthumbnail`_
- Pluggable Key Value Store support (cached db, redis, and dynamodb by AWS)
- Pluggable Backend support
- Admin integration with possibility to delete
- Dummy generation (placeholders)
- Flexible, simple syntax, generates no html
- ImageField for model that deletes thumbnails (only compatible with django 1.2.5 or less)
- CSS style cropping options
- Back smart cropping, and remove borders from the images when cropping
- Margin calculation for vertical positioning
- Alternative resolutions versions of a thumbnail

Read more in `the documentation (latest version) <http://sorl-thumbnail.rtfd.org/>`_

Developers
==========

|jazzband|

This is a `Jazzband <https://jazzband.co>`_ project. By contributing you agree to
abide by the `Contributor Code of Conduct <https://jazzband.co/about/conduct>`_
and follow the `guidelines <https://jazzband.co/about/guidelines>`_.

Feel free to create a new Pull request if you want to propose a new feature.
If you need development support or want to discuss with other developers
join us in the channel #sorl-thumnbnail at freenode.net or Gitter.

For releases updates and more in deep development discussion use our mailing list
in Google Groups.

- IRC Channel: irc://irc.freenode.net/#sorl-thumbnail

- Mailing List: sorl-thumbnail@googlegroups.com https://groups.google.com/d/forum/sorl-thumbnail

Tests
-----
The tests should run with tox and pytest. Running `tox` will run all tests for all environments.
However, it is possible to run a certain environment with `tox -e <env>`, a list of all environments
can be found with `tox -l`. These tests require the dependencies of the different engines defined in
the documentation. It is possible to install these dependencies into a vagrant image with the
Vagrantfile in the repo.

User Support
============

If you need help using sorl-thumbnail browse http://stackoverflow.com/questions/tagged/sorl-thumbnail
and posts your questions with the `sorl-thumbnail` tag.


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

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.sites',
        'django.contrib.comments',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.contenttypes',

        'sorl.thumbnail',
    ]


Templates Usage
---------------

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
value store and its thumbnail references and the thumbnail files when deleted.
Please note that this is only compatible with django 1.2.5 or less.::

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

Using in combination with other thumbnailers
--------------------------------------------

Alternatively, you load the templatetags by {% load sorl_thumbnail %}
instead of traditional {% load thumbnail %}. It's especially useful in
projects that do make use of multiple thumbnailer libraries that use the
same name (``thumbnail``) for the templatetag module::

    {% load sorl_thumbnail %}
    {% thumbnail item.image "100x100" crop="center" as im %}
        <img src="{{ im.url }}" width="{{ im.width }}" height="{{ im.height }}">
    {% endthumbnail %}

Frequently asked questions
==========================

Is so slow in Amazon S3!
------------------------

Possible related to the implementation of your Amazon S3 Backend, see the `issue #351`_
due the storage backend reviews if there is an existing thumbnail when tries to
generate the thumbnail that makes an extensive use of the S3 API

A fast workaround if you are not willing to tweak your storage backend is to set::

   THUMBNAIL_FORCE_OVERWRITE = True

So it will avoid to overly query the S3 API.


.. |gh-actions| image:: https://github.com/jazzband/sorl-thumbnail/workflows/Test/badge.svg
    :target: https://github.com/jazzband/sorl-thumbnail/actions
.. |docs| image:: https://readthedocs.org/projects/pip/badge/?version=latest
    :alt: Documentation for latest version
    :target: http://sorl-thumbnail.rtfd.org/en/latest/
.. |pypi| image:: https://img.shields.io/pypi/v/sorl-thumbnail.svg
    :target: https://pypi.python.org/pypi/sorl-thumbnail
    :alt: sorl-thumbnail on PyPI
.. |codecov| image:: https://codecov.io/gh/jazzband/sorl-thumbnail/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/jazzband/sorl-thumbnail
   :alt: Coverage
.. |jazzband-badge| image:: https://jazzband.co/static/img/badge.svg
   :target: https://jazzband.co/
   :alt: Jazzband
.. |jazzband| image:: https://jazzband.co/static/img/jazzband.svg
   :target: https://jazzband.co/
   :alt: Jazzband

.. _`Pillow`: http://pillow.readthedocs.org/en/latest/
.. _`ImageMagick`: http://www.imagemagick.org/script/index.php
.. _`PIL`: http://www.pythonware.com/products/pil/
.. _`Wand`: http://docs.wand-py.org/
.. _`pgmagick`: http://pgmagick.readthedocs.org/en/latest/
.. _`vipsthumbnail`: http://www.vips.ecs.soton.ac.uk/index.php?title=VIPS

.. _`Template examples`: http://sorl-thumbnail.readthedocs.org/en/latest/examples.html#template-examples
.. _`Model examples`: http://sorl-thumbnail.readthedocs.org/en/latest/examples.html#model-examples
.. _`Low level API examples`: http://sorl-thumbnail.readthedocs.org/en/latest/examples.html#low-level-api-examples
.. _`issue #351`: https://github.com/jazzband/sorl-thumbnail/issues/351
.. _`Django supported versions policy`: https://www.djangoproject.com/download/#supported-versions
