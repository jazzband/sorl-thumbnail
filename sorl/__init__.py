# -*- encoding: utf8 -*-
from __future__ import unicode_literals

import logging

__author__ = "Mikko Hellsing"
__license__ = "BSD"
__version__ = '13.0'
__maintainer__ = "Mario César Señoranis Ayala"
__email__ = "mariocesar@creat1va.com"
__status__ = "Production"


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# Add a logging handler that does nothing to silence messages with no logger
# configured
logging.getLogger('sorl').addHandler(NullHandler())
