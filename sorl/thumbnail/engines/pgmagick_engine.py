from pgmagick import Blob, ColorspaceType, Geometry, Image, ImageType, \
    OrientationType
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
        image = Image(blob)
        orientation = image.orientation()

        if orientation in (OrientationType.UndefinedOrientation,
            OrientationType.TopLeftOrientation):
            pass
        elif orientation == OrientationType.TopRightOrientation:
            image.flop()
        elif orientation == OrientationType.BottomRightOrientation:
            image.rotate(180.)
        elif orientation == OrientationType.BottomLeftOrientation:
            image.flip()
        elif orientation == OrientationType.LeftTopOrientation:
            image.rotate(90.).flip()
        elif orientation == OrientationType.RightTopOrientation:
            image.rotate(90.)
        elif orientation == OrientationType.RightBottomOrientation:
            image.rotate(90.).flop()
        elif orientation == OrientationType.LeftBottomOrientation:
            image.rotate(270.)

        image.orientation(OrientationType.TopLeftOrientation)

        return image

    def get_image_size(self, image):
        geometry = image.size()
        return geometry.width(), geometry.height()

    def is_valid_image(self, raw_data):
        blob = Blob()
        blob.update(raw_data)
        im = Image(blob)
        return im.isValid()

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            image.type(ImageType.TrueColorMatteType)
            image.quantizeColorSpace(ColorspaceType.RGBColorspace)
        elif colorspace == 'GRAY':
            image.type(ImageType.GrayscaleMatteType)
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

