# encoding=utf-8
from __future__ import unicode_literals

import logging

__author__ = "Mikko Hellsing"
__license__ = "BSD"
__version__ = '12.3'
__maintainer__ = "Mario César Señoranis Ayala"
__email__ = "mariocesar@humanzilla.com"
__status__ = "Production/Stable"


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# Add a logging handler that does nothing to silence messages with no logger
# configured
logging.getLogger('sorl').addHandler(NullHandler())
