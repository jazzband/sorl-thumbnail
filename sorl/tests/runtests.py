#!/usr/bin/env python
import os
import sys
from os.path import abspath, dirname, join as pjoin


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
here = abspath(dirname(__file__))

paths = [
    pjoin(here, os.pardir, os.pardir),
]
for path in paths:
    sys.path.insert(0, path)

from django.test.simple import run_tests


def thumbnail_tests():
    apps = ['test_app']
    failures = run_tests(apps, verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    thumbnail_tests()

