from setuptools import setup, find_packages
from setuptools.command.test import test


class TestCommand(test):
    def run(self):
        from tests.runtests import runtests

        runtests()


setup(
    name='sorl-thumbnail',
    use_scm_version=True,
    description='Thumbnails for Django',
    long_description=open('README.rst').read(),
    author="Mikko Hellsing",
    author_email='mikko@aino.se',
    maintainer="Jazzband",
    maintainer_email="roadies@jazzband.co",
    license="BSD",
    url='https://github.com/jazzband/sorl-thumbnail',
    packages=find_packages(exclude=['tests', 'tests.*']),
    platforms='any',
    python_requires='>=3.6',
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
    ],
    cmdclass={"test": TestCommand},
    setup_requires=['setuptools_scm'],
)
