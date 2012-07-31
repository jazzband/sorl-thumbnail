from cStringIO import StringIO
from sorl.thumbnail.engines.base import EngineBase

try:
    from PIL import Image, ImageFile, ImageDraw
except ImportError:
    import Image, ImageFile, ImageDraw


class Engine(EngineBase):
    def get_image(self, source):
        buf = StringIO(source.read())
        return Image.open(buf)

    def get_image_size(self, image):
        return image.size

    def is_valid_image(self, raw_data):
        buf = StringIO(raw_data)
        try:
            trial_image = Image.open(buf)
            trial_image.verify()
        except Exception:
            return False
        return True

    def _orientation(self, image):
        try:
            exif = image._getexif()
        except (AttributeError, KeyError, IndexError):
            exif = None
        if exif:
            orientation = exif.get(0x0112)
            if orientation == 2:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                image = image.rotate(180)
            elif orientation == 4:
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            elif orientation == 5:
                image = image.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                image = image.rotate(-90)
            elif orientation == 7:
                image = image.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                image = image.rotate(90)
        return image

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            if image.mode == 'RGBA':
                return image # RGBA is just RGB + Alpha
            if image.mode == 'P' and 'transparency' in image.info:
                return image.convert('RGBA')
            return image.convert('RGB')
        if colorspace == 'GRAY':
            return image.convert('L')
        return image

    def _scale(self, image, width, height):
        return image.resize((width, height), resample=Image.ANTIALIAS)

    def _crop(self, image, width, height, x_offset, y_offset):
        return image.crop((x_offset, y_offset,
                           width + x_offset, height + y_offset))

    def _get_raw_data(self, image, format_, quality, progressive=False):
        ImageFile.MAXBLOCK = 1024 * 1024 * 2
        buf = StringIO()
        params = {
            'format': format_,
            'quality': quality,
            'optimize': 1,
        }
        if format_ == 'JPEG' and progressive:
            params['progressive'] = True
        try:
            image.save(buf, **params)
        except IOError:
            params.pop('optimize')
            image.save(buf, **params)
        raw_data = buf.getvalue()
        buf.close()
        return raw_data

