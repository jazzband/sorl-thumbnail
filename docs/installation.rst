********************
Installation & Setup
********************

Installation
============
First you need to make sure to read the :doc:`requirements`. To install
sorl-thumbnail is easy::

    pip install sorl-thumbnail

Or you can go to `the github page <https://github.com/sorl/sorl-thumbnail>`_

Setup
=====

.. highlight:: python

1. Add ``sorl.thumbnail`` to your ``settings.INSTALLED_APPS``.
2. Configure your ``settings``
3. If you are using the cached database key value store you need to sync the
   database::

    python manage.py makemigrations thumbnail
    python manage.py migrate

