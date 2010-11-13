How does sorl-thumbnail operate
===============================

When you use the ``thumbnail`` template tag sorl-thumbnail looks up the
thumbnail in a :ref:`kvstore-requirements`. The key for a thumbnail is
generated from its filename and storage. The thumbnail filename in turn is
generated from the source and requested thumbnail size and options.  If the key
for the thumbnail is found in the |kvstore|, the serialized thumbnail
information is fetched from it and returned. If the thumbnail key is not found
there sorl-thumbnail continues to generate the thumbnail and stores necesssary
information in the |kvstore|.  It is worth noting that sorl-thumbnail does not
check if source or thumbnail exists if the thumbnail key is found in the
|kvstore|.

.. note:: This means that if you change or delete a source file or delete the
    thumbnail, sorl-thumbnail will still fetch from the |kvstore|.
    Therefore it is important that if you delete or change a source or
    thumbnail file notify the |kvstore|.

If you change or delete a source or a thumbnail for some reason, you can use
the ``KVStoreBase`` sublass's ``delete`` method. Alternatively if you have
**deleted** a file you can use the management command :ref:`thumbnail-cleanup`.
Deleting an image using the ``sorl.thumbnail.ImageField`` will notify the
|kvstore| to delete references to it and delete all of its thumbnail references
and files.

**Why you ask?** Why go through all the trouble with a |kvstore| and risk
stale cache?

The reason is speed and especially with storages other than local file storage.
Checking if a file exists before serving it will cost too much.

.. note:: We have to assume the thumbnail exists if the thumbnail key exists in
    the |kvstore|

There are bonuses, we can store meta data in the |kvstore| that would be
too costly to retreive even for local file storage. Today this meta data
consists only of the image size but this could be expanded to for example EXIF
data.

`Overview of how things are done
<https://docs.google.com/drawings/edit?id=1wlE4LkQpzXd2a2Nxfjt6_j5NG7889dzMyf0V-xPAJSE&hl=en>`_

.. |kvstore| replace:: Key Value Store

