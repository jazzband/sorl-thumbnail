import sys

try:
    if sys.version_info >= (3, 8):  # Python 3.8+
        import importlib.metadata as importlib_metadata
    else:
        import importlib_metadata

    __version__ = importlib_metadata.version("sorl-thumbnail")
except Exception:
    pass