from PIL import Image, Image
from cStringIO import StringIO
from sorl.thumbnail.engines.base import ThumbnailEngineBase


class ThumbnailEngine(ThumbnailEngineBase):
    def get_image(self, source):
        buf = StringIO(source.open().read())
        return Image.open(buf)

    def get_image_size(self, image):
        return image.size

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            return image.convert('RGB')
        if colorspace == 'GRAY':
            return image.convert('L')
        return image

    def _resize(self, image, width, height):
        return image.resize((width, height), resample=Image.ANTIALIAS)

    def _crop(self, image, width, height, x_offset, y_offset):
        return image.crop((x_offset, y_offset,
                           width + x_offset, height + y_offset))

    def _write(self, image, format_, quality, thumbnail):
        Image.MAXBLOCK = 1024 * 1024
        buf = StringIO()
        try:
            image.save(buf, format=format_, quality=quality, optimize=1)
        except IOError:
            image.save(buf, format=format_, quality=quality)
        thumbnail.write(buf.getvalue())
        buf.close()

