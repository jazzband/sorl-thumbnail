from pgmagick import Image, Blob, ColorspaceType, Geometry
from cStringIO import StringIO
from sorl.thumbnail.engines.base import ThumbnailEngineBase
from sorl.thumbnail.helpers import toint
from sorl.thumbnail.parsers import parse_geometry, parse_crop
from django.core.files.storage import FileSystemStorage


class ThumbnailEngine(ThumbnailEngineBase):
    def _get_image(self, source):
        blob = Blob()
        blob.update(source.read())
        return Image(blob)

    def _get_image_dimensions(self, image):
        geomatry = image.size()
        return geometry.width(), geometry.height()

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            image.quantizeColorSpace(ColorspaceType.RGBColorspace)
        elif colorspace == 'GRAY':
            image.quantizeColorSpace(ColorspaceType.GRAYColorspace)
        image.quantize()
        return image

    def _resize(self, image, width, height):
        geometry = Geometry(width, height)
        return image.scale(geometry)


