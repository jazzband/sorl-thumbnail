from PIL import Image, ImageFilter, ImageChops
from sorl.thumbnail import utils
import re


def dynamic_import(names):
    imported = []
    for name in names:
        # Use rfind rather than rsplit for Python 2.3 compatibility.
        lastdot = name.rfind('.')
        modname, attrname = name[:lastdot], name[lastdot + 1:]
        mod = __import__(modname, {}, {}, [''])
        imported.append(getattr(mod, attrname))
    return imported


def get_valid_options(processors):
    """
    Returns a list containing unique valid options from a list of processors
    in correct order.
    """
    valid_options = []
    for processor in processors:
        if hasattr(processor, 'valid_options'):
            valid_options.extend([opt for opt in processor.valid_options
                                  if opt not in valid_options])
    return valid_options


def colorspace(im, requested_size, opts):
    if 'bw' in opts and im.mode != "L":
        im = im.convert("L")
    elif im.mode not in ("L", "RGB", "RGBA"):
        im = im.convert("RGB")
    return im
colorspace.valid_options = ('bw',)


def autocrop(im, requested_size, opts):
    if 'autocrop' in opts:
        bw = im.convert("1")
        bw = bw.filter(ImageFilter.MedianFilter)
        # white bg
        bg = Image.new("1", im.size, 255)
        diff = ImageChops.difference(bw, bg)
        bbox = diff.getbbox()
        if bbox:
            im = im.crop(bbox)
    return im
autocrop.valid_options = ('autocrop',)


def scale_and_crop(im, requested_size, opts):
    x, y = [float(v) for v in im.size]
    xr, yr = [float(v) for v in requested_size]

    if 'crop' in opts or 'max' in opts:
        r = max(xr / x, yr / y)
    else:
        r = min(xr / x, yr / y)

    if r < 1.0 or (r > 1.0 and 'upscale' in opts):
        im = im.resize((int(x * r), int(y * r)), resample=Image.ANTIALIAS)

    crop = opts.get('crop') or 'crop' in opts
    if crop:
        # Difference (for x and y) between new image size and requested size.
        x, y = [float(v) for v in im.size]
        dx, dy = (x - min(x, xr)), (y - min(y, yr))
        if dx or dy:
            # Center cropping (default).
            ex, ey = dx / 2, dy / 2
            box = [ex, ey, x - ex, y - ey]
            # See if an edge cropping argument was provided.
            edge_crop = (isinstance(crop, basestring) and
                           re.match(r'(?:(-?)(\d+))?,(?:(-?)(\d+))?$', crop))
            if edge_crop and filter(None, edge_crop.groups()):
                x_right, x_crop, y_bottom, y_crop = edge_crop.groups()
                if x_crop:
                    offset = min(x * int(x_crop) / 100, dx)
                    if x_right:
                        box[0] = dx - offset
                        box[2] = x - offset
                    else:
                        box[0] = offset
                        box[2] = x - (dx - offset)
                if y_crop:
                    offset = min(y * int(y_crop) / 100, dy)
                    if y_bottom:
                        box[1] = dy - offset
                        box[3] = y - offset
                    else:
                        box[1] = offset
                        box[3] = y - (dy - offset)
            # See if the image should be "smart cropped".
            elif crop == 'smart':
                left = top = 0
                right, bottom = x, y
                while dx:
                    slice = min(dx, 10)
                    l_sl = im.crop((0, 0, slice, y))
                    r_sl = im.crop((x - slice, 0, x, y))
                    if utils.image_entropy(l_sl) >= utils.image_entropy(r_sl):
                        right -= slice
                    else:
                        left += slice
                    dx -= slice
                while dy:
                    slice = min(dy, 10)
                    t_sl = im.crop((0, 0, x, slice))
                    b_sl = im.crop((0, y - slice, x, y))
                    if utils.image_entropy(t_sl) >= utils.image_entropy(b_sl):
                        bottom -= slice
                    else:
                        top += slice
                    dy -= slice
                box = (left, top, right, bottom)
            # Finally, crop the image!
            im = im.crop([int(v) for v in box])
    return im
scale_and_crop.valid_options = ('crop', 'upscale', 'max')


def filters(im, requested_size, opts):
    if 'detail' in opts:
        im = im.filter(ImageFilter.DETAIL)
    if 'sharpen' in opts:
        im = im.filter(ImageFilter.SHARPEN)
    return im
filters.valid_options = ('detail', 'sharpen')
