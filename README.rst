sorl-thumbnail
==============

Thumbnails for Django. Totally rewritten.

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

Read more in `the documentation (latest version) <http://thumbnail.sorl.net/>`_

Usage
=====

Everything documented here: http://thumbnail.sorl.net/ and::

    <img src="{% thumbnail obj.image "200x150" crop="center" %}"/>

