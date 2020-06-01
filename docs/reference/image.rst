*********
ImageFile
*********

.. highlight:: html+django

``ImageFile`` is an image abstraction that contains useful attributes when
working with images. The ``thumbnail`` template tag puts the generated thumbnail
in context as an ``ImageFile`` instance. In the following example::

    {% thumbnail item.image "100x100" as im %}
        <img src="{{ im.url }}">
    {% endthumbnail %}

``im`` will be an ``ImageFile`` instance.

.. highlight:: python

ImageFile attributes
====================

``name``
--------
Name of the image as returned from the underlying storage.

``storage``
-----------
Returns the storage instance.

``width``
---------
Returns the width of the image in pixels.

``x``
-----
Alias of ``width``

``height``
----------
Returns the height of the image in pixels.

``y``
-----
Alias of ``height``

``ratio``
---------
Returns the image ratio (y/x) as a float

``url``
-------
URL of the image url as returned by the underlying storage.

``src``
-------
Alias of ``url``

``size``
--------
Returns the image size in pixels as a (x, y) tuple

``key``
-------
Returns a unique key based on ``name`` and ``storage``.


ImageFile methods
=================

``exists``
----------
Returns whether the file exists as returned by the underlying storage.

``is_portrait``
---------------
Returns ``True`` if ``y > x``, else ``False``

``set_size``
------------
Sets the size of the image, takes an optional size tuple (x, y) as argument.

``read``
--------
Reads the file as done from the underlying storage.

``write``
---------
Writes content to the file. Takes content as argument. Content is either raw
data or an instance of ``django.core.files.base.ContentFile``.

``delete``
----------
Deletes the file from underlying storage.

``serialize``
-------------
Returns a serialized version of self.

``serialize_storage``
---------------------
Returns the ``self.storage`` as a serialized dot name path string.

