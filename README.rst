django-thumbnail
==============

A fork of sorl-thumbnail; created due to its inactivity.

---------------------------------------------------------

Format preservation has been added. To preserve format set settings.THUMBNAIL_PRESERVE_FORMAT = True.
Gracefully degrades and defaults to using settings.THUMBNAIL_FORMAT.
Applications that currently use sorl should not notice any difference in functionality unless settings.THUMBNAIL_PRESERVE_FORMAT is set explicitly set to True.