from os import makedirs
from os.path import isfile, isdir, getmtime, dirname

from PIL import Image, ImageFilter

from methods import autocrop

# Boolean options for the Thumbnail class.
OPTIONS = ['crop', 'autocrop', 'upscale', 'bw', 'detail', 'sharpen']

class ThumbnailException(Exception):
    pass

class Thumbnail(object):
    def __init__(self, source_path, thumbnail_path, dimensions, quality=85,
                 generate_thumbnail=True, force_update=False, options):
        
        # Ensure the source file exists
        if not isfile(self.source_path):
            raise ThumbnailException('Source file does not exist')
        
        # Full file paths
        self.source_path    = source_path
        self.thumbnail_path = thumbnail_path
        
        # Thumbnail settings
        self.size    = size
        self.quality = quality

        # Thumbnail options
        for o in options:
            if o not in OPTIONS:
                raise TypeError('Thumbnail received an invalid keyword argument: %s' % k)
        for o in OPTIONS:
            setattr(self, o, o in options)

        self.force_update = force_update
        if generate_thumbnail:
            self.generate_thumbnail()


    def _get_thumbnail(self):
        if not hasattr(self, '_thumbnail'):
            try:
                self._thumbnail = Image.open(self.thumbnail_path)
            except IOError, detail:
                raise ThumbnailException(detail)
        return self._thumbnail
    thumbnail = property(_get_thumbnail)


    def _get_source(self):
        if not hasattr(self, '_source'):
            try:
                self._source = Image.open(self.source_path)
            except IOError, detail:
                raise ThumbnailException(detail)
        return self._source
    source = property(_get_source)


    def generate_thumbnail(self):
        if not isfile(self.thumbnail_path) or self.force_update or \
                getmtime(self.source_path) > getmtime(self.thumbnail_path):
            
            # Ensure the directory exists
            directory = dirname(self.thumbnail_path)
            if not isdir(directory):
                try:
                    makedirs(directory)
                except IOError, detail:
                    raise ThumbnailException(detail)
            
            self._make_thumbnail()
            return True
        return False


    def _make_thumbnail(self):
        im = self.source

        if self.bw and im.mode != "L":
            im = im.convert("L")
        elif im.mode not in ("L", "RGB"):
            im = im.convert("RGB")

        if self.autocrop:
            im = autocrop(im)

        x, y   = [float(v) for v in im.size]
        xr, yr = [float(v) for v in self.size]

        if self.crop:
            r = max(xr/x, yr/y)
        else:
            r = min(xr/x, yr/y)

        if not self.upscale:
            r = min(r,1)
        im = im.resize((int(x*r), int(y*r)), resample=Image.ANTIALIAS)

        if self.crop:
            x, y   = [float(v) for v in im.size]
            ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
            im = im.crop((int(ex), int(ey), int(x-ex), int(y-ey)))

        if self.detail:
            im = im.filter(ImageFilter.DETAIL)

        if self.sharpen:
            im = im.filter(ImageFilter.SHARPEN)

        try:
            im.save(self.thumbnail_path, "JPEG", quality=self.quality,
                    optimize=1)
        except IOError:
            # Try again, without optimization (the JPEG library can't optimize
            # an image which is larger than ImageFile.MAXBLOCK which is 64k by
            # default)
            try:
                im.save(self.thumbnail_path, "JPEG", quality=self.quality)
            except IOError, detail:
                raise ThumbnailException(detail)
