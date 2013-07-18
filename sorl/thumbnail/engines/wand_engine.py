'''
Wand (>=v0.3.0) engine for Sorl-thumbnail
'''

from wand.image import Image
from sorl.thumbnail.engines.base import EngineBase


class Engine(EngineBase):
    def get_image(self, source):
        return Image(blob=source.read())

    def get_image_size(self, image):
        return image.size

    def is_valid_image(self, raw_data):
        im = Image(blob=raw_data)
        return im.isValid()

    def _orientation(self, image):
        orientation = image.orientation
        if orientation == 'top_right':
            image.flop()
        elif orientation == 'bottom_right':
            image.rotate(degree=180)
        elif orientation == 'bottom_left':
            image.flip()
        elif orientation == 'left_top':
            image.rotate(degree=90)
            image.flop()
        elif orientation == 'right_top':
            image.rotate(degree=90)
        elif orientation == 'right_bottom':
            image.rotate(degree=-90)
            image.flop()
        elif orientation == 'left_bottom':
            image.rotate(degree=-90)
        image.orientation = 'top_left'
        return image

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            image.type = 'truecolormatte'
        elif colorspace == 'GRAY':
            image.type = 'grayscalematte'
        else:
            return image
        return image

    def _scale(self, image, width, height):
        image.resize(width, height)
        return image

    def _crop(self, image, width, height, x_offset, y_offset):
        image.crop(width, height, width=x_offset, height=y_offset)
        return image

    def _get_raw_data(self, image, format_, quality, progressive=False):
        image.compression_quality = quality
        if format_ == 'JPEG' and progressive:
            image.format = 'pjpeg'
        return image.make_blob()
