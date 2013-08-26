import sorl
from setuptools import setup, find_packages
from setuptools.command.test import test


setup(
    name='django-thumbnail',
    version=sorl.__version__,
    description='Thumbnailing in Django',
    long_description=open('README.rst').read(),
    author='Clinton Christian',
    author_email='pygeek@me.com',
    license='BSD',
    url='https://github.com/pygeek/django-thumbnail',
    packages=find_packages(exclude=['tests', 'tests.*']),
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics',
        'Framework :: Django',
    ],
)

