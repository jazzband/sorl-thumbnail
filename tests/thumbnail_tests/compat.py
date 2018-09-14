import platform


def is_osx():
    return platform.system() == 'Darwin'


def is_windows():
    return platform.system() == 'Windows'
