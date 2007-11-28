class ThumbnailException(Exception):
    pass

class ThumbnailInvalidImage(ThumbnailException):
    pass

class ThumbnailIOError(ThumbnailException):
    pass

class ThumbnailOSError(ThumbnailException):
    pass
