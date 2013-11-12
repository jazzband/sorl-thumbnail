Thumbnails for Django. The original and the best

.. image:: https://secure.travis-ci.org/mariocesar/sorl-thumbnail.png?branch=master :target: https://travis-ci.org/mariocesar/sorl-thumbnail

Features at a glance
--------------------
- Storage support
- Pluggable Engine support (ImageMagick, PIL, pgmagick included)
- Pluggable Key Value Store support (cached db, redis)
- Pluggable Backend support
- Admin integration with possibility to delete
- Dummy generation (placeholders)
- Flexible, simple syntax, generates no html
- ImageField for model that deletes thumbnails
- CSS style cropping options
- Margin calculation for vertical positioning

Read more in `the documentation (latest version) <http://sorl-thumbnail.rtfd.org/>`_

Format preservation has been added. To preserve format set settings.THUMBNAIL_PRESERVE_FORMAT = True.

Gracefully degrades and defaults to using settings.THUMBNAIL_FORMAT.

Applications that currently use sorl should not notice any difference in functionality unless settings.THUMBNAIL_PRESERVE_FORMAT is set explicitly set to True.

=====
Usage
=====

Everything documented here: http://thumbnail.sorl.net/ and::

    <img src="{% thumbnail obj.image "200x150" crop="center" %}"/>
