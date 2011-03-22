from pgmagick import Blob, Color, ColorspaceType, DrawableLine
from pgmagick import DrawableRectangle, Geometry, Image
from sorl.thumbnail.engines.base import EngineBase

try:
    from pgmagick._pgmagick import get_blob_data
except ImportError:
    from base64 import b64decode
    def get_blob_data(blob):
        return b64decode(blob.base64())


class Engine(EngineBase):
    def get_image(self, source):
        blob = Blob()
        blob.update(source.read())
        return Image(blob)

    def get_image_size(self, image):
        geometry = image.size()
        return geometry.width(), geometry.height()

    def dummy_image(self, width, height):
        d = self._get_dummy_image_data(width, height)
        im = Image(Geometry(width, height), Color(*d['canvas_color']))
        im.strokeColor(Color(*d['line_color']))
        im.strokeWidth(1)
        for line in d['lines']:
            im.draw(DrawableLine(*line))
        im.fillColor(Color())
        im.draw(DrawableRectangle(*d['rectangle']))
        return im

    def is_valid_image(self, raw_data):
        blob = Blob()
        blob.update(raw_data)
        im = Image(blob)
        return im.isValid()

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
        image.magick(format_.encode('utf8'))
        image.quality(quality)
        blob = Blob()
        image.write(blob)
        return get_blob_data(blob)

