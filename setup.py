from os.path import abspath, dirname, join as pjoin
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


fn = abspath(pjoin(dirname(__file__), 'README.rst'))
fp = open(fn, 'r')
long_description = fp.read()
fp.close()

setup(
    name='sorl-thumbnail',
    version='10.12-beta2',
    url='https://github.com/sorl/sorl-thumbnail',
    license='BSD',
    author='Mikko Hellsing',
    author_email='mikko@aino.se',
    description='Thumbnails for Django',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics',
        'Framework :: Django',
    ],
    packages=[
        'sorl',
        'sorl.thumbnail',
        'sorl.thumbnail.conf',
        'sorl.thumbnail.engines',
        'sorl.thumbnail.kvstores',
        'sorl.thumbnail.templatetags',
    ],
    platforms='any',
    # we don't want eggs
    zip_safe=False,
)

