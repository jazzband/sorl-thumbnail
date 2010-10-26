from PIL import Image, ImageFile
from cStringIO import StringIO
from sorl.thumbnail.engines.base import ThumbnailEngineBase
from sorl.thumbnail.helpers import parse_geometry, toint


class ThumbnailEngine(ThumbnailEngineBase):
    def resize(self, image, geometry, options):
        x = float(image.size[0])
        y = float(image.size[1])
        crop = options['crop']
        upscale = options['upscale']
        requested_x, requested_y = parse_geometry(geometry)
        # set requested_x or requested_y proportionally if not set
        if requested_x is None:
            requested_x = x * requested_y / y
        elif requested_y is None:
            requested_y = y * requested_x / x
        # calculate scaling factor
        factors = (requested_x / x, requested_y / y)
        factor = max(factors) if crop else min(factors)
        if factor <= 1 or upscale:
            new_x = toint(x * factor)
            new_y = toint(y * factor)
            image = image.resize((new_x, new_y), resample=Image.ANTIALIAS)
        return image
        # 
        #if '^' in geometry.modifiers and crop:
        #    if x > requested_x:
        #        if crop.endswith('West'):
        #            carg = (0, 0, requested_x, y)
        #        elif crop.endswith('East'):
        #            carg = (x - requested_x, 0, x, y)
        #        else:
        #            # center
        #            x1 = (x - requested_x) / 2
        #            x2 = x - x1
        #            if (x - requested_x) % 2:
        #                x2 -= 1
        #            carg = (x1, 0, x2, y)
        #    elif y > requested_y:
        #        if crop.startswith('North'):
        #            carg = (0, 0, x, y - requested_y)
        #        elif crop.endswith('South'):
        #            carg = (0, y - requested_y, x, y)
        #        else:
        #            # center
        #            y1 = (y - requested_y) / 2
        #            y2 = y - y1
        #            if (y - requested_y) % 2:
        #                y2 -= 1
        #            carg = (0, y1, x, y2)
        #    else:
        #        return
        #    self.im = self.im.crop(carg)

    def colorspace(self, image, geometry, options):
        colorspace = options['colorspace']
        if colorspace == 'RGB':
            return image.convert('RGB')
        if colorspace == 'GRAY':
            return image.convert('L')
        return image

    def create(self, source, geometry, options, thumbnail):
        buf = StringIO(source.open().read())
        image = Image.open(buf)
        image = self.colorspace(image, geometry, options)
        image = self.resize(image, geometry, options)
        self.write(image, options, thumbnail)
        buf.close()
        return thumbnail

    def write(self, image, options, thumbnail):
        format_ = options['format']
        quality = options['quality']
        ImageFile.MAXBLOCK = 1024 * 1024
        buf = StringIO()
        try:
            image.save(buf, format=format_, quality=quality, optimize=1)
        except IOError:
            image.save(buf, format=format_, quality=quality)
        thumbnail.save(buf.getvalue())
        buf.close()
        return thumbnail

