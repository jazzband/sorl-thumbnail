*******************
Management commands
*******************

.. highlight:: python

.. _thumbnail-cleanup:

thumbnail cleanup
=================
``python manage.py thumbnail cleanup``

This cleans up the Key Value Store from stale cache. It removes references to
images that do not exist and thumbnail references and their actual files for
images that do not exist. It removes thumbnails for unknown images.


.. _thumbnail-clear:

thumbnail clear
===============
``python manage.py thumbnail clear``

This totally empties the Key Value Store from all keys that start with the
``settings.THUMBNAIL_KEY_PREFIX``. It does not delete any files. It is generally safe to
run this if you do not reference the generated thumbnails by name somewhere
else in your code. The Key Value store will update when you hit the template
tags, and if the thumbnails still exist they will be used and not overwritten.

If you want to have all your thumbnails re-generated, e.g. when changing your backend,
you can use the option ``--delete`` or ``-d`` to empty the Key Value Store and have
all thumbnails removed as well.
