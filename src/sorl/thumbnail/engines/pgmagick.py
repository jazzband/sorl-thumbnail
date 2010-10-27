from pgmagick import Image, Blob, ColorspaceType
from cStringIO import StringIO
from sorl.thumbnail.engines.base import ThumbnailEngineBase
from sorl.thumbnail.helpers import toint
from sorl.thumbnail.parsers import parse_geometry, parse_crop
from django.core.files.storage import FileSystemStorage


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
        if factor < 1 or upscale:
            new_x = toint(x * factor)
            new_y = toint(y * factor)
            image = image.resize((new_x, new_y), resample=Image.ANTIALIAS)
        if not crop or crop == 'noop':
            return image
        crop_args = parse_crop(crop, (new_x, new_y),
                               (requested_x, requested_y))
        return image.crop(crop_args)

    def colorspace(self, image, geometry, options):
        colorspace = options['colorspace']
        if colorspace == 'RGB':
            image.quantizeColorSpace(ColorspaceType.RGBColorspace)
        elif colorspace == 'GRAY':
            image.quantizeColorSpace(ColorspaceType.GRAYColorspace)
        image.quantize()
        return image

    def create(self, source, geometry, options, thumbnail):
        blob = Blob()
        blob.update(source.read())
        image = Image(blob)
        image = self.colorspace(image, geometry, options)
        image = self.resize(image, geometry, options)
        self.write(image, options, thumbnail)
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

