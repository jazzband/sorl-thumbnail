Installation & Setup
====================

Installation
------------
First you need to make sure to read the :doc:`requirements`. To install
sorl-thumbnail is easy::

    pip install sorl-thumbnail

Or you can go to `the github page <https://github.com/sorl/sorl-thumbnail>`_

Setup
-----
1. Add ``sorl.thumbnail`` to your ``settings.INSTALLED_APPS``.
2. Configure your ``settings``
3. If you are using the cached database key value store you need to sync the
   database::

    python manage.py syncdb

4. If you want to use the dummy generation feature add the following to your
   urls.py::

    (r'^', include('sorl.thumbnail.urls')),

   This will not do anything unless you have ``THUMBNAIL_DUMMY`` set to
   ``True``. You also need to set your IP in the ``INTERNAL_IPS`` setting, for
   example::

    INTERNAL_IPS = ('127.0.0.1',)

