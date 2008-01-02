==============
sorl.thumbnail
==============

The ``sorl.thumbnail`` package, provides a way of thumbnailing images.

It requires the Python Imaging Library (PIL_).

To enable PDF thumbnails you need ImageMagick_ and to enable Word document
thumbnails you need both wvWare_ and ImageMagick_.

.. _PIL: http://www.pythonware.com/products/pil/
.. _ImageMagick: http://www.imagemagick.org/
.. _wvWare: http://wvware.sourceforge.net/


{% thumbnail %} template tag
============================

The usual way to use thumbnails with this package is to use the
``{% thumbnail %}`` template tag.

To use this tag, add ``'sorl.thumbnail'`` to your ``INSTALLED_APPS`` setting.
Once you've done that, use ``{% load thumbnail %}`` in a template to give your
template access to the tag.

Basic usage
-----------

The thumbnail tag creates the thumbnail if it didn't exist (or if the source
image was modified more recently than the existing thumbnail) and then returns
the absolute url of the thumbnail (``MEDIA_URL`` + relative thumbnail
url). The basic usage is::

    {% thumbnail [source-filename] [size] [options] %}

``source-filename`` must a variable containing the path of an existing image (or
other supported format), relative to``MEDIA_ROOT``.

``size`` can either be:

    - the size in the format ``[width]x[height]`` (for example,
      ``{% thumbnail source 100x50 %}``) or
    
    - a variable containing a two element list of the width and height (for
      example, ``{% thumbnail source size %}`` will look for a template context
      variable named ``size`` containing something like ``[100, 50]``).

``options`` are optional (obviously) and should be comma separated (without a
space between them - for example, ``crop,bw,quality=95``). Valid options are:

    ``quality=[1-100]``
      Alter the quality of the JPEG thumbnail (the default is 85).

    ``crop``
      Crop the source image height or width to exactly match the requested
      thumbnail size (the default is to proportionally resize the source image
      to fit within the requested thumbnail size).

    ``autocrop``
      Remove any unnecessary whitespace from the edges of the source image.
      This occurs before the crop or propotional resize.

    ``bw``
      Make the thumbnail grayscale (not really just black & white).

    ``upscale``
      Allow upscaling of the source image during scaling.

    ``sharpen``
      Sharpen the thumbnail image (using the PIL sharpen filter)

    ``detail``
      Add detail to the image, like a mild ``sharpen`` (using the PIL detail
      filter)

An example of basic usage::

    <img src="{% thumbnail person.photo 80x80 crop,upscale %}" />

Advanced usage
--------------

The thumbnail tag can also place a ``DjangoThumbnail`` object on the context,
providing access to the properties of the thumbnail such as the height and
width::

    {% thumbnail [source-filename] [size] [options] as [variable] %}

When ``as [variable]`` is used, the tag does not return the absolute url of the
thumbnail. The variable (containing the ``DjangoThumbnail`` object) has the
following useful methods and properties:

    ``absolute_url``
      The absolute url of the thumbnail (the ``__unicode__`` method of this
      object also returns the absolute url, so you can also just do
      ``{{ thumbnail_variable }}``).

    ``relative_url``
      The relative url (to MEDIA_URL) of the thumbnail.
    
    ``width`` and ``height``
      The width/height of the thumbnail image.

    ``filesize``
      The file size (in bytes) of the thumbnail.
      To output user-friendly file sizes, use the included `filesize filter`_
      (or Django's built-in more simplistic ``filesizeformat`` filter).

    ``source_width`` and ``source_height``
      The width/height of the source image.

    ``source_filesize``
      The file size of the source. Has same methods as ``filesize``.


An example of advanced usage::

    {% thumbnail person.photo 250x250 bw,autocrop as thumb %}
    <img src="{{ thumb }}" width="{{ thumb.width }}" height="{{ thumb.height }}" />

Debugging the thumbnail tag
---------------------------

By default, if there is an error creating the thumbnail or resolving the image
variable (1st argument) then the thumbnail tag will just return an empty string.
And if there was a context variable to be set it will also be set to an empty
string.

For example, you will not see an error if the thumbnail could not be written
to directory because of permissions error.

To display those errors rather than failing silently, add a ``THUMBNAIL_DEBUG``
property to your settings module and set it to ``True``::

	THUMBNAIL_DEBUG = True

PDF and Word document thumbnails
--------------------------------

PDF conversion is done with ImageMagick's `convert` program. The default
location where ``sorl.thumbnail`` will look for this program is
`/usr/bin/convert`.

Word documents are converted to a PostScript file with wvWare's `wvps` program.
The default location where ``sorl.thumbnail`` will look for this program is
`/usr/bin/wvPS`. This file is then converted to an image with ImageMagick's
`convert` program.

To specify an alternate location for either of these programs, add the relevant
property to your settings module::

	THUMBNAIL_CONVERT = '/path/to/imagemagick/convert'
	THUMBNAIL_WVPS = '/path/to/wvPS'


Thumbnail filenames
===================

The thumbnail filename is generated from the source filename, the target size,
any options provided and the quality.

For example, ``{% thumbnail "1.jpg" 80x80 crop,bw %}`` will save the
thumbnail image as::

    MEDIA_ROOT + '1_jpg_80x80_crop_bw_q85.jpg'

By default, thumbnails are saved in the same directory as the source image.
You can override this behaviour by adding one or more of the following
properties to your settings module:

    ``THUMBNAIL_BASEDIR``
      Save thumbnail images to a directory directly off ``MEDIA_ROOT``,
      still keeping the relative directory structure of the source image.

    ``THUMBNAIL_SUBDIR``
      Save thumbnail images to a sub-directory relative to the source image.

    ``THUMBNAIL_PREFIX``
      Prepend thumnail filenames with the specified prefix.

For example, if the tag was ``{% thumbnail "photos/1.jpg" 150x150 %}`` then
``THUMBNAIL_BASEDIR = 'thumbs'`` would save the thumbnail as::

    MEDIA_ROOT + '/thumbs/photos/1_jpg_150x150_q85.jpg'

or ``THUMBNAIL_SUBDIR = '_thumbs'`` would save the thumbnail as::

    MEDIA_ROOT + '/photos/_thumbs/1_jpg_150x150_q85.jpg'

or ``THUMBNAIL_PREFIX = '__'`` would save the thumbnail as::

    MEDIA_ROOT + '/photos/__1_jpg_150x150_q85.jpg'


Changing the default JPEG quality
=================================

If you would rather your thumbnail images have a different default JPEG
quality than 85, add a ``THUMBNAIL_QUALITY`` property to your settings module.
For example::

    THUMBNAIL_QUALITY = 95

This will only affect images which have not be explicitly given a quality
option.


``filesize`` filter
===================

This filter returns the number of bytes in either the nearest unit or a specific
unit (depending on the chosen format method).
    
Use this filter to output user-friendly file sizes. For example::

	{% thumbnail source 200x200 as thumb %}
	Thumbnail file size: {{ thumb.size|filesize }}

If the generated thumbnail size came to 2000 bytes, this would output
"Thumbnail file size: 1.9 KiB" (the filter's default format is ``auto1024``).
You can specify a different format like so:

	{{ thumb.size|filesize:"auto1000long" }}

Which would output "2 kilobytes".

Acceptable formats are:

auto1024, auto1000
  convert to the nearest unit, appending the abbreviated unit name to the string
  (e.g. '2 KiB' or '2 kB').
  auto1024 is the default format.

auto1024long, auto1000long
  convert to the nearest multiple of 1024 or 1000, appending the correctly
  pluralized unit name to the string (e.g. '2 kibibytes' or '2 kilobytes').

kB, MB, GB, TB, PB, EB, ZB or YB
  convert to the exact unit (using multiples of 1000).

KiB, MiB, GiB, TiB, PiB, EiB, ZiB or YiB
  convert to the exact unit (using multiples of 1024).

The auto1024 and auto1000 formats return a string, appending the correct unit to
the value. All other formats return the floating point value.


Advanced usage
==============

Some helpful methods are provided in the ``sorl.thumbnail.utils`` module. One
example of using these could be to clean up any thumbnails belonging solely to
a model in its ``delete()`` method.

Use the ``DjangoThumbnail`` class in ``sorl.thumbnail.main`` if you want
behaviour similar to the ``{% thumbnail %}`` tag (i.e. using the ``MEDIA_ROOT``
and ``MEDIA_URL``) in your Python code. If you want to use a different file
naming method, just subclass and override the ``_get_relative_thumbnail``
method.

Use the ``Thumbnail`` class in ``sorl.thumbnail.base`` for more low-level
creation of thumbnails. This class doesn't have any Django-specific ties.
