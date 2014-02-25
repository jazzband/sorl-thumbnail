# -*- encoding: utf8 -*-
import sorl
from setuptools import setup, find_packages
from setuptools.command.test import test


class TestCommand(test):
    def run(self):
        from tests.runtests import runtests

        runtests()


setup(
    name='sorl-thumbnail',
    version=sorl.__version__,
    description='Thumbnails for Django',
    long_description=open('README.rst').read(),
    author=sorl.__author__,
    author_email='mikko@aino.se',
    maintainer=sorl.__maintainer__,
    maintainer_email=sorl.__email__,
    license=sorl.__license__,
    url='https://github.com/mariocesar/sorl-thumbnail',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics',
        'Framework :: Django',
    ],
    cmdclass={"test": TestCommand},
)

