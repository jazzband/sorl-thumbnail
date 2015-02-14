import sys
import platform

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


if PY3:
    import unittest
else:
    from django.utils import unittest


def is_osx():
    return platform.system() == 'Darwin'


def is_windows():
    return platform.system() == 'Windows'
