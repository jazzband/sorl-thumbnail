from PIL import Image, ImageFile
from cStringIO import StringIO
from sorl.thumbnail.engines.base import ThumbnailEngineBase


class ThumbnailEngine(ThumbnailEngineBase):
    def _get_image(self, source):
        buf = StringIO(source.open().read())
        return Image.open(buf)

    def _get_image_dimensions(self, image):
        return image.size

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            return image.convert('RGB')
        if colorspace == 'GRAY':
            return image.convert('L')
        return image

    def _resize(self, image, width, height):
        return image.resize((width, height), resample=Image.ANTIALIAS)

    def _crop(self, image, width, height, offset_x, offset_y):
        return image.crop((offset_x, offset_y, width + offset_x, height + offset_y))

    def _write(self, image, format_, quality, thumbnail):
        ImageFile.MAXBLOCK = 1024 * 1024
        buf = StringIO()
        try:
            image.save(buf, format=format_, quality=quality, optimize=1)
        except IOError:
            image.save(buf, format=format_, quality=quality)
        thumbnail.save(buf.getvalue())
        buf.close()

