from ..PIL import Image, ImageDraw
from cStringIO import StringIO
from sorl.thumbnail.engines.base import EngineBase


class Engine(EngineBase):
    def get_image(self, source):
        buf = StringIO(source.read())
        return Image.open(buf)

    def get_image_size(self, image):
        return image.size

    def dummy_image(self, width, height):
        im = Image.new('L', (width, height), 240)
        draw = ImageDraw.Draw(im)
        draw.line((0, 0, width, height), fill=128)
        draw.line((0, height, width, 0), fill=128)
        del draw
        return im

    def is_valid_image(self, raw_data):
        buf = StringIO(raw_data)
        try:
            trial_image = Image.open(buf)
            trial_image.verify()
        except Exception:
            return False
        return True

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            return image.convert('RGB')
        if colorspace == 'GRAY':
            return image.convert('L')
        return image

    def _scale(self, image, width, height):
        return image.resize((width, height), resample=Image.ANTIALIAS)

    def _crop(self, image, width, height, x_offset, y_offset):
        return image.crop((x_offset, y_offset,
                           width + x_offset, height + y_offset))

    def _get_raw_data(self, image, format_, quality):
        Image.MAXBLOCK = 1024 * 1024
        buf = StringIO()
        try:
            image.save(buf, format=format_, quality=quality, optimize=1)
        except IOError:
            image.save(buf, format=format_, quality=quality)
        raw_data = buf.getvalue()
        buf.close()
        return raw_data

