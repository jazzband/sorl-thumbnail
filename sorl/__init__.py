import logging


__version__ = '11.121'
VERSION = tuple(map(int, __version__.split('.')))


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# Add a logging handler that does nothing to silence messages with no logger
# configured
logging.getLogger('sorl').addHandler(NullHandler())


