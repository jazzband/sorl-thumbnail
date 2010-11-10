from base64 import b64decode
from ..pgmagick import Blob, Color, ColorspaceType, DrawableLine, Geometry
from ..pgmagick import Image
from sorl.thumbnail.engines.base import EngineBase


class Engine(EngineBase):
    def get_image(self, source):
        blob = Blob()
        blob.update(source.read())
        return Image(blob)

    def get_image_size(self, image):
        geometry = image.size()
        return geometry.width(), geometry.height()

    def dummy_image(self, width, height):
        im = Image(Geometry(width, height), Color(240, 240, 240))
        im.strokeColor(Color(128, 128, 128))
        im.strokeWidth(1)
        im.draw(DrawableLine(0, 0, width, height))
        im.draw(DrawableLine(0, height, height, 0))
        return im

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            image.quantizeColorSpace(ColorspaceType.RGBColorspace)
        elif colorspace == 'GRAY':
            image.quantizeColorSpace(ColorspaceType.GRAYColorspace)
        else:
            return image
        image.quantize()
        return image

    def _scale(self, image, width, height):
        geometry = Geometry(width, height)
        image.scale(geometry)
        return image

    def _crop(self, image, width, height, x_offset, y_offset):
        geometry = Geometry(width, height, x_offset, y_offset)
        image.crop(geometry)
        return image

    def _get_raw_data(self, image, format_, quality):
        image.magick(format_)
        image.quality(quality)
        blob = Blob()
        image.write(blob)
        # is there a better way?
        return b64decode(blob.base64())

