#!/usr/bin/env python
import os
import sys
from django.conf import settings
from os.path import abspath, dirname, join as pjoin


def runtests(verbosity=1, interactive=True, failfast=True, settings_module=None):
    here = abspath(dirname(__file__))
    root = pjoin(here, os.pardir)
    sys.path[0:0] = [ here, root, pjoin(root, 'sorl') ]
    if settings_module is not None:
        settings_modules = [ settings_module ]
    else:
        settings_modules = [ 'settings.%s' % s for s in (
            'pil', 'pgmagick', 'imagemagick', 'grephicsmagick', 'redis') ]
    failures = 0
    for settings_module in settings_modules:
        print "Running tests for '%s'" % settings_module
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
        from django.test.utils import get_runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(
            verbosity=verbosity, interactive=interactive, failfast=failfast
            )
        failures += test_runner.run_tests(settings.INSTALLED_APPS)
    return failures

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Runs the test suite for sorl-thumbnail.'
        )
    parser.add_argument(
        '--settings',
        dest='settings_module',
        action='store',
        help='Specify settings module.',
        )
    parser.add_argument(
        '--noinput',
        dest='interactive',
        action='store_false',
        default=True,
        help='Do not prompt the user for input of any kind.',
        )
    parser.add_argument(
        '--failfast',
        dest='failfast',
        action='store_true',
        default=False,
        help='Stop running the test suite after first failed test.',
    )
    args = parser.parse_args()
    failures = runtests(
        verbosity=1,
        interactive=args.interactive,
        failfast=args.failfast,
        settings_module=args.settings_module,
        )
    if failures:
        sys.exit(bool(failures))

