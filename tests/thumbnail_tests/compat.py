import platform

try:
    import unittest2 as unittest
except ImportError:
    import unittest


def is_osx():
    return platform.system() == 'Darwin'


def is_windows():
    return platform.system() == 'Windows'
