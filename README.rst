News
====

2013-11-12
----------
@mariocesar: We have a new team of mantainers for sorl-thumbnail. I wan't to encourage
all developers that have fixes, forks and new features to talk in the irc channel of
the project. irc://freenode.net/#sorl-thumbnail


2013-11-09
----------

@nikko: Unfortunately I no longer work with Django so my motivation to keep developing
for sorl-thumbnail is very low. If you are interested in taking over this
project please send an email to mikko@aino.se explaing why you are the perfect
fit for owning this project.

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

Read more in `the documentation (latest version)
<http://sorl-thumbnail.rtfd.org/>`_

Format preservation has been added. To preserve format set settings.THUMBNAIL_PRESERVE_FORMAT = True.
Gracefully degrades and defaults to using settings.THUMBNAIL_FORMAT.

Applications that currently use sorl should not notice any difference in functionality unless settings.THUMBNAIL_PRESERVE_FORMAT is set explicitly set to True.

=====
Usage
=====

Everything documented here: http://thumbnail.sorl.net/ and::

    <img src="{% thumbnail obj.image "200x150" crop="center" %}"/>

