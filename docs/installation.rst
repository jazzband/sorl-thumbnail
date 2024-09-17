********************
Installation & Setup
********************

Installation
============
First you need to make sure to read the :doc:`requirements`. To install
sorl-thumbnail::

    pip install sorl-thumbnail

Depending of the chosen image backend, you may also use one of::

    pip install sorl-thumbnail[pil]
    pip install sorl-thumbnail[wand]
    pip install sorl-thumbnail[pgmagick]

Setup
=====

.. highlight:: python

1. Add ``sorl.thumbnail`` to your ``settings.INSTALLED_APPS``.
2. Configure your ``settings``
3. If you are using the cached database key value store you need to sync the
   database::

    python manage.py migrate

