from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("sorl-thumbnail").version
except DistributionNotFound:
    pass
