# -*- encoding: utf8 -*-
import logging

__author__ = "Mikko Hellsing"
__license__ = "BSD"
__version__ = '12.0'
__maintainer__ = u"Mario César Señoranis Ayala"
__email__ = "mariocesar@creat1va.com"
__status__ = "Production"


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# Add a logging handler that does nothing to silence messages with no logger
# configured
logging.getLogger('sorl').addHandler(NullHandler())
