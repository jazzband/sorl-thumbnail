=========
Changelog
=========

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


12.4
====

Although you can find references to this version number in the Git history of
this project, this version was never released to PyPI.


12.4a1
======

This is the most recent release of this project to PyPI before the migration to
Jazzband.
