Management commands
===================


.. _thumbnail-cleanup:

thumbnail cleanup
-----------------
``python manage.py thumbnail cleanup``

This cleans up the Key Value Store from stale cache. It removes references to
images that do not exist and thumbnail references and their acual files for
images that do not exist. It removes thumbnails for unknown images.


.. _thumbnail-clear:

thumbnail clear
---------------
``python manage.py thumbnail clear``

This totally empties the Key Value Store from all keys that start with the
:ref:`THUMBNAIL_KEY_PREFIX`. It does not delete any files. It is generally safe to
run this if you do not reference the generated thumbnails by name somewhere
else in your code. The Key Value store will update when you hit the template
tags, and if the thumbnails still exist they will be used and not overwritten.

