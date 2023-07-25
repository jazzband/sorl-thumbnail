from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sorl-thumbnail")
except PackageNotFoundError:
    # package is not installed
    pass

