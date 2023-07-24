try:
    import importlib.metadata as importlib_metadata
    __version__ = importlib_metadata.version("sorl-thumbnail")
except Exception:
    pass
