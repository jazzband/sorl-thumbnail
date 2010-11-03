from kaa import imlib2
from cStringIO import StringIO
from sorl.thumbnail.engines.base import EngineBase


class Engine(EngineBase):
    def get_image(self, source):
        return imlib2.open_from_memory(source.read())

    def get_image_size(self, image):
        return image.size

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            return image.convert('RGB')
        if colorspace == 'GRAY':
            return image.convert('L')
        return image

    def _scale(self, image, width, height):
        return image.scale((width, height))

    def _crop(self, image, width, height, x_offset, y_offset):
        return image.crop((x_offset, y_offset), (width, height))

    def _write(self, image, format_, quality, thumbnail):
        buf = image.get_raw_data(write=True)
        thumbnail.write(buf)

