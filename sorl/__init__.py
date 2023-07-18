try:
    # Python 3.8+
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata

__version__ = importlib_metadata.version("sorl-thumbnail")