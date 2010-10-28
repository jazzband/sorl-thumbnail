from base64 import b64decode
from pgmagick import Image, Blob, ColorspaceType, Geometry
from sorl.thumbnail.engines.base import ThumbnailEngineBase


class ThumbnailEngine(ThumbnailEngineBase):
    def _get_image(self, source):
        blob = Blob()
        blob.update(source.read())
        return Image(blob)

    def _get_image_size(self, image):
        geometry = image.size()
        return geometry.width(), geometry.height()

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            image.quantizeColorSpace(ColorspaceType.RGBColorspace)
        elif colorspace == 'GRAY':
            image.quantizeColorSpace(ColorspaceType.GRAYColorspace)
        else:
            return image
        image.quantize()
        return image

    def _resize(self, image, width, height):
        geometry = Geometry(width, height)
        image.scale(geometry)
        return image

    def _crop(self, image, width, height, x_offset, y_offset):
        geometry = Geometry(width, height, x_offset, y_offset)
        image.crop(geometry)
        return image

    def _write(self, image, format_, quality, thumbnail):
        image.magick(format_)
        image.quality(quality)
        blob = Blob()
        image.write(blob)
        # is there a better way?
        thumbnail.write(b64decode(blob.base64()))

