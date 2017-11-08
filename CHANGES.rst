=========
Changelog
=========

12.0 (TBA)
==========

* [Feature] #480 ``sorl_thumbnail`` alias for ``thumbnail`` templatetag module 
  added to allow usage in combination with other thumbnailers.
* [Feature] #145 Python 3 support
* [Feature] #165 Django 1.5-1.6 support
* [Feature] #308 Django 1.7
* [Feature] #290 New DBM based Key-Value Store
* [Feature] Cropbox option
* [Feature] Rounded corners
* [Feature] Vagrant testing
* [Feature] #89 ``THUMBNAIL_URL_TIMEOUT`` setting for retrieving an image with a URL
* [Feature] #97 New style tag ``<img src="{% thumbnail obj.image "200x150" crop="center" %}"/>``
* [Feature] Blur support for (PIL) engine
* [Feature] ``background_margin`` filter
* [Feature] #135 Ability to preserve file format
* [Feature] #159 Wand engine
* [Feature] #178 Improved error logging in templates
* [Feature] #176 Custom CACHE storage
* [Feature] #191 Added text filters ``markdown_thumbnails`` and ``html_thumbnails``
* [Feature] #187 Padding around the thumbnail
* [Feature] #201 Flatten images (imagemagick)
* [Fix] #73 Multipage PDFs and animated GIF support (imagemagick)
* [Fix] #78 Bad resize when upscale is off and image is small
* [Fix] Multiple docs fixes
* [Fix] #82 ``ValueError`` errors in orientation (imagemagick)
* [Fix] #83 ``open()`` calls on windows (imagemagick)
* [Fix] #92 Improved interaction with S3 storage engine
* [Fix] #94 Display thumbnail if it exists, even if ``THUMBNAIL_DUMMY`` is ``True``
* [Fix] #98 #137 #113 Exif errors (PIL)
* [Fix] #129 #214 Support for very large images (PIL)
* [Fix] #39 ``get_thumbnail`` doesn't respect ``THUMBNAIL_DUMMY`` setting
* [Fix] Thumbnail error occurring when file is blank (40fe1b0)
* [Fix] #148 Error in thumbnail clear command, when storage is empty
* [Fix] #139 Proper UrlStorage url to prevent HTTP Error 505
* [Fix] #162 Sporadic IntegrityError when calling get_thumbnail
* [Fix] #116 KeyError when Image file raw data is not a valid image
* [Fix] #186 Better expetion handling for ``AdminImageWidget``
* [Fix] #192 Fixes photo desaturation issue (PIL)
* [Fix] #203 Remove check if file exists from the templatetag code
* [Fix] #213 Fixed descriptor leak (imagemagick)
* [Fix] #216 #217 Fixed OSError handling (PIL)
* [Fix] #304 #14 Fix AdminWidget
* [Fix] #274 Fix issue with transparent PNGs: IOError("cannot use transparency for this mode")
* [Fix] #265 Better support for LA mode images in PIL engine
* [Fix] #261 THUMBNAIL_DEBUG has False as default 
