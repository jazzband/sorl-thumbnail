from cStringIO import StringIO
from PIL import Image, ImageFilter, ImageFile
from sorl.thumbnail.backends.base import ThumbnailBackendBase


def rndint(number):
    if isinstance(number, float):
        number = round(number, 0)
    return int(number)


class ThumbnailBackend(ThumbnailBackendBase):
    def __init__(self, fobj):
        self.fobj = fobj
        buf = StringIO(fobj.read())
        self.im = Image.open(buf)

    @property
    def width(self):
        return self.im.size[0]
    x = width

    @property
    def height(self):
        return self.im.size[1]
    y = height

    def resize(self, geometry, crop=None):
        x = geometry.x
        y = geometry.y
        # set x or y proportionally if not set
        if x is None:
            x = self.x * float(y) / self.y
        elif y is None:
            y = self.y * float(x) / self.x
        # we will need these values for crop
        requested_x = rndint(x)
        requested_y = rndint(y)
        x = float(x)
        y = float(y)
        if '!' not in geometry.modifiers:
            # keep aspect ratio
            # calculate resizing factor r
            rarg = (x / self.x, y / self.y)
            r = max(*rarg) if '^' in geometry.modifiers else min(*rarg)
            x = self.x * r
            y = self.y * r
        # both x and y need to be int (whole pixels)
        x = rndint(x)
        y = rndint(y)

        if '>' in geometry.modifiers and not (self.x > x or self.y > y):
            return
        if '<' in geometry.modifiers and not (self.x > x and self.y > y):
            return

        self.im = self.im.resize((x, y), resample=Image.ANTIALIAS)

        if '^' in geometry.modifiers and crop:
            if x > requested_x:
                if crop.endswith('West'):
                    carg = (0, 0, requested_x, y)
                elif crop.endswith('East'):
                    carg = (x - requested_x, 0, x, y)
                else:
                    # center
                    x1 = (x - requested_x) / 2
                    x2 = x - x1
                    if (x - requested_x) % 2:
                        x2 -= 1
                    carg = (x1, 0, x2, y)
            elif y > requested_y:
                if crop.startswith('North'):
                    carg = (0, 0, x, y - requested_y)
                elif crop.endswith('South'):
                    carg = (0, y - requested_y, x, y)
                else:
                    # center
                    y1 = (y - requested_y) / 2
                    y2 = y - y1
                    if (y - requested_y) % 2:
                        y2 -= 1
                    carg = (0, y1, x, y2)
            else:
                return
            self.im = self.im.crop(carg)

    def colorspace(self, value):
        if value == 'RGB':
            self.im = self.im.convert('RGB')
        if value == 'GRAY':
            self.im = self.im.convert('L')

    def sharpen(self, value):
        # TODO make better use of the value parameter
        if value:
            self.im = self.im.filter(ImageFilter.SHARPEN)

    def write(self, name, storage, format=None, quality=None, **kwargs):
        buf = StringIO()
        ImageFile.MAXBLOCK = 1024 * 1024
        try:
            self.im.save(buf, format=format, quality=quality, optimize=1)
        except IOError:
            self.im.save(buf, format=format, quality=quality)
        storage.save(buf.getvalue())
        buf.close()

