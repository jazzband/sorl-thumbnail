from distutils.core import setup
 
setup(
    name = 'sorl-thumbnail',
    version = '3.2.2',
    url = 'http://code.google.com/p/sorl-thumbnail/',
    download_url = 'http://sorl-thumbnail.googlecode.com/files/sorl-thumbnail-3.2.2.tar.gz',
    description = 'Thumbnails for Django',
    packages = [
        'sorl',
        'sorl.thumbnail',
        'sorl.thumbnail.templatetags',
        'sorl.thumbnail.tests',
        'sorl.thumbnail.management',
        'sorl.thumbnail.management.commands',
    ],
)
