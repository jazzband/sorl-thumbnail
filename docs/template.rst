
Template tags and filters
=========================

.. highlight:: html+django

Sorl-thumbnail comes with one template tag `thumbnail`_ and two filters:
`is_portrait`_ and `margin`_. To use any of them in you templates you first
need to load them::

    {% load thumbnail %}


.. _thumbnail:

thumbnail
---------

Syntax::

    {% thumbnail source geometry [key1=value1, key2=value2...] as var %}
    {% endthumbnail %}

Alternative syntax using empty::

    {% thumbnail source geometry [key1=value1, key2=value2...] as var %}
    {% empty %}
    {% endthumbnail %}

The ``{% empty %}`` section is rendered if the thumbnail source is resolved to
an empty value.


.. _source:

Source
^^^^^^

.. highlight:: python

Source can be an ImageField, FileField, a file name (assuming default_storage),
a url. What we need to know is name and storage, see how ImageFile figures
these things out::

    class ImageFile(BaseImageFile):
        _size = None

        def __init__(self, file_, storage=None):
            if not file_:
                raise ThumbnailError('File is empty.')
            # figure out name
            if hasattr(file_, 'name'):
                self.name = file_.name
            else:
                self.name = force_unicode(file_)
            # figure out storage
            if storage is not None:
                self.storage = storage
            elif hasattr(file_, 'storage'):
                self.storage = file_.storage
            elif url_pat.match(self.name):
                self.storage = UrlStorage()
            else:
                self.storage = default_storage

Geometry
^^^^^^^^

.. highlight:: html+django

Geometry is specified as ``widthxheight``, ``width`` or ``xheight``.
Width and height are in pixels. Geometry can either be a string or resolve
into a valid geometry string. Examples::

    {% thumbnail item.image "200x100" as im %}
        <img src="{{ im.src }}">
    {% endthumbnail %}

    {% thumbnail item.image "200" as im %}
        <img src="{{ im.src }}">
    {% endthumbnail %}

    {% thumbnail item.image "x100" as im %}
        <img src="{{ im.src }}">
    {% endthumbnail %}

    {% thumbnail item.image geometry as im %}
        <img src="{{ im.src }}">
    {% endthumbnail %}

If width and height are given the image is rescaled to maximum values of height
and width given. Aspect ratio preserved.


Options
^^^^^^^
Options are passed on to the backend and engine, the backend generates the
thumbnail filename from it and the engine can use it for processing. Option
keys are not resolved in context but values are. Passing all options to the
engine means that you can easily subclass an engine and create new features
like rounded corners or what ever processing you like. The options described
below are how they are used and interperated in the shipped engines.

``crop``
~~~~~~~~
This option is only used if both width and height is given. Crop behaves much
like `css background-position`_.  The image is first rescaled to minimum values
of height and width given, this will be equivalent to the `padding box` in the
above text. After it is rescaled it will apply the cropping options. There are
some differences to the `css background-position`_:

- Only % and px are valid lengths (units)
- ``noop`` (No Operation) is a valid option which means there is no 
  cropping after the initial rescaling to minimum of width and height.

There are many overlapping options here for example ``center`` is equivalent to
``50%``. There is not a problem with that in it self but it is a bit of a
problem if you will for sorl-thumbnail. Sorl-thumbnail will generate a new
thumbnail for every unique source, geometry and options.  This is a design
choice because we want to stay flexible with the options and not interpret them
anywhere else but in the engine methods. In clear words, be consistent in your
cropping options if you don't want to generate unnecessary thumbnails. In case
you are wondering, sorl-thumbnail sorts the options so the order does not
matter, same options but in different order will generate only one thumbnail.

``upscale``
~~~~~~~~~~~
Upscale is a boolean and controls if the image can be upscaled or not. For
example if your source is 100x100 and you request a thumbnail of size 200x200
and upscale is False this will reurn a thumbnail of size 100x100. If upscale
was True this would result in a thumbnail size 200x200 (upscaled). The default
value is True.

``quality``
~~~~~~~~~~~
Quality is a value between 0-100 and controls the thumbnail write quality.
Default value is 95.

``format``
~~~~~~~~~~
This controls the the write format and thumbnail extension. Formats supported
by the shipped eninges are JPEG and PNG. Default value is JPEG.

``colorspace``
~~~~~~~~~~~~~~
This controls the resulting thumbnails colorspace, valid values are: RGB and
GRAY. Default value is RGB

``options``
~~~~~~~~~~~
Yes this option is called ``options``. This needs to be a context variable that
resolves to a dictionary. This dictionary can contain multiple options, for
example::

    options = {'colorspace': 'GRAY', 'quality': 75, 'crop': 'center'}

You can use this option together with the other options but beware that the
order will matter. As soon as the keyword ``options`` is encountered all the
options that have a key in ``options`` are overwritten. Similarly, options in
the ``options`` dict will be overwritten by options set after the options
keyword argument to the thumbnail tag.


is_portrait
-----------
This filter returns True if the image height is larger than the image width.
Examples::

    {% thumbnail item.image "100x100" %}
    {% if item.image|is_portrait %}
        <div class="portrait">
            <img src="{{ im.url }}">
        </div>
    {% else %}
        <div class="landscape">
            <img src="{{ im.url }}">
        </div>
    {% endif %}
    {% endthumbnail %}

    {% if item.image|is_portrait %}
        {% thumbnail item.image "100x200" crop="center" %}
            <img src="{{ im.url }}">
        {% endthumbnail %}
    {% else %}
        {% thumbnail item.image "100x200" crop="center" %}
            <img src="{{ im.url }}">
        {% endthumbnail %}
    {% endif %}


margin
------
Margin is a filter for calculating margins agains a padding box. For example
lets say you have an image ``item.image`` and you want to pad it vertically in
a 1000x1000 box, you would simply write::

    <div class="millxmill">
        <img src="{{ item.image.url }}" style="margin:{{ item.image|margin:"1000x1000" }}">
    </div>

The above is a rather syntetic example the more common usecase is when you want
boxes of images of a certain size but you do not want to crop them::

    {% for profile in profiles %}
    <div>
        {% thumbnail profile.photo "100x100" as im %}
            <img src="{{ im.url }}" style="margin:{{ im|margin:"100x100" }}">
        {% empty %}
            <img src="ghost100x100.jpg">
        {% endthumbnail %}
    </div>
    {% enfor %}

The more problematic is to get the top margin, however the margin filter
outputs all values.

.. _css background-position: http://www.w3.org/TR/CSS2/colors.html#propdef-background-position

