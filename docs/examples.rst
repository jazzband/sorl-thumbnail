Examples
========

Template examples
-----------------

.. highlight:: html+django

All of the examples assume that you first load the ``thumbnail`` template tag in
your template::

    {% load thumbnail %}

Simple::

    {% thumbnail item.image "100x100" crop="center" as im %}
        <img src="{{ im.url }}" width="{{ im.width }}" height="{{ im.height }}">
    {% endthumbnail %}

    
Crop using margin filter, x, y aliases::

    {% thumbnail item.image "100x700" as im %}
        <img style="margin:{{ im|margin:"100x700" }}" src="{{ im.url }}" width="{{ im.x }}" height="{{ im.y }}">
    {% endthumbnail %}

Using external images and advanced cropping::

    {% thumbnail "http://www.aino.se/media/i/logo.png" "40x40" crop="80% top" as im %}
        <img src="{{ im.url }}">
    {% endthumbnail %}

Using the empty feature, the empty section is rendered when the source is
resolved to an empty value or an invalid image source, you can think of it as
rendering when the thumbnail becomes undefined::

    {% thumbnail item.image my_size_string crop="left" as im %}
        <img src="{{ im.url }}">
    {% empty %}
        <p>No image</p>
    {% endthumbnail %}

Nesting tags and setting size (geometry) for width only::

    {% thumbnail item.image "1000" as big %}
        {% thumbnail item.image "50x50" crop="center" as small %}
            <a href="{{ big.url}}" title="look ma!"><img src="{{ small.url }}"></a>
        {% endthumbnail %}
    {% endthumbnail %}

Setting geometry for height only::

    {% thumbnail item.image "x300" as im %}
        <img src="{{ im.url }}">
    {% endthumbnail %}

Setting format and using the is_portrait filter::

    {% if item.image|is_portrait %}
        <div class="portrait">
        {% thumbnail item.image "100" crop="10px 10px" format="PNG" as im %}
            <img src="{{ im.url }}">
        {% endthumbnail %}
        </div>
    {% else %}
        <div class="landscape">
        {% thumbnail item.image "50" crop="bottom" format="PNG" as im %}
            <img src="{{ im.url }}">
        {% endthumbnail %}
        </div>
        <div>
            <p>Undefined behaviour</p>
        </div>
    {% endif %}


Model examples
--------------

.. highlight:: python

Using the ImageField that automatically deletes references to itself in the key
value store and ts thumbnail references and the thumbnail files when deleted::

    from django.db import models
    from sorl.thumbnail import ImageField

    class Item(models.Model):
        image = ImageField()


.. note:: You do not need to use the ``sorl.thumbnail.ImageField`` to use
    ``sorl.thumbnail``. The standard ``django.db.models.ImageField`` is fine
    except that it does not know how to delete itself from the Key Value Store
    or its thumbnails if you delete it.

