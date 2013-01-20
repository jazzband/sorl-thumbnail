from cStringIO import StringIO
from sorl.thumbnail.engines.base import EngineBase

try:
    from PIL import Image, ImageFile, ImageDraw, ImageChops
except ImportError:
    import Image, ImageFile, ImageDraw, ImageChops


def round_corner(radius, fill):
    """Draw a round corner"""
    corner = Image.new('L', (radius, radius), 0) #(0, 0, 0, 0))
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner
 
def round_rectangle(size, radius, fill):
    """Draw a rounded rectangle"""
    width, height = size
    rectangle = Image.new('L', size, 255) #fill)
    corner = round_corner(radius, 255) #fill)
    rectangle.paste(corner, (0, 0))
    rectangle.paste(corner.rotate(90), (0, height - radius)) # Rotate the corner and paste it
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    return rectangle


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

    def _cropbox(self, image, x, y, x2, y2):
        return image.crop((x, y, x2, y2))

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

    def _rounded(self, image, r):
        i = round_rectangle(image.size, r, "notusedblack")
        image.putalpha(i)
        return image

    def _get_raw_data(self, image, format_, quality, progressive=False):
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
            try:
                # Temporary encrease ImageFile MAXBLOCK
                maxblock = ImageFile.MAXBLOCK
                ImageFile.MAXBLOCK = image.size[0] * image.size[1]
                image.save(buf, **params)
            except IOError:
                params.pop('optimize')
                image.save(buf, **params)
            finally:
                ImageFile.MAXBLOCK = maxblock
        raw_data = buf.getvalue()
        buf.close()
        return raw_data

