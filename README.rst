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
