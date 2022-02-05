=======
Changes
=======

12.8.0
======
* Drop support for Django 3.0.
* Added support for Django 3.2 and 4.0.
* Confirmed Python 3.9 and 3.10 support.
* Adapted size regex getting size from the identify output. #532
* Display possible ``thumbnail`` command labels in command help.
* Added Jazzband code of conduct.


12.7.0
======
* Drop support for Django 1.11
* Added support for Django 3.1
* Moved to GitHub Action for continuous integration.
* Correction in convert_engine with unknown exif orientation
* Using more resilient _get_exif_orientation logic in convert engine
* Update wand_engine.py for ImageMagick 7
* Fix cannot write mode RGBA as JPEG when thumbnailing a GIF


12.6.3
======

* Deprecate Python 2 compatibility shims in favor of Python 3 only codebase. #623
* Fix README on notes about ImageField cleaning up references on delete. #624
* Fix image ratios with EXIF orientation. #619
* Fix test coverage tracking. #622 and #617


12.6.2
======

* Fix rST syntax errors from 12.6.0 and 12.6.1 that blocked release. #613
* Improve QA setup and add rST validation to Travis and tox test matrix. #613


12.6.1
======

* Deprecate explicit support for Python 3.4 and 3.5 in order to simplify the test matrix #610
* Add requirement for ``setuptools_scm`` to automatically resolve version from git tags #610
* Removed property ``thumbnail.__version__`` #610


12.6.0
======

* Add Cropbox feature in Wand/Convert Engine
* Add testing for Django 2.2
* Remove "django.utils.six" to support Django 3.0+
* Remove Python 2 support


12.5.0
======

* Make the template tag accept a falsey image
* Update identify (of convert_engine) for faster multi-page PDF thumbnailing
* Fix Redis KVStore timeout
* Fix format conversion in Wand engine
* Added setting THUMBNAIL_REMOVE_URL_ARGS
* Add testing for Django 2.1
* Drop support for Django < 1.11
* Added ssl parameter to Redis object instantiation
* Fix 2 ResourceWarning: unclosed file, in tests
* Fix AdminImageWidget with Django 2.1
* Test in release version of Python 3.7
* Remove unused unittest imports in thumbnail_tests.compat
* Add a __str__ method to ImageFile


12.4.1
======

sorl-thumbnail was welcomed into the `Jazzband organization and project
<https://jazzband.co/>`__. Jazzband is open to all, and any member of Jazzband
can contribute directly to sorl-thumbnail's GitHub repo. We hope this will
encourage more open source programmers to contribute. Thank you @mariocesar for
taking this step and for the years of effort in this project.

12.4.1 is the first release on PyPI since the migration to the Jazzband
project, and includes two years' worth of changes. Thank you to all
contributors. These are some of the highlights:

* Target Django versions are now 1.8, 1.10, 1.11 and 2.0
* Target Python versions are now 2.7, 3.3, 3.4, 3.5 and 3.6
* Enable GIF support (#263)
* Enable WebP support (#460)
* New ``sorl_thumbnail`` templatetag library that mirrors traditional ``thumbnail``
* Fix bug RGBA mode not compatible with JPEG on PILLOW >=3.7 (#503)
* Don't check EXIF orientation with GraphicsMagick
* Bug fix for handling non-ASCII characters in filenames (#434)
* Better error detection and handling in some cases (#492)
* Improve automated testing
* Improve documentation
