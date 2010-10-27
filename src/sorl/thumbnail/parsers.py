#coding=utf-8
import re
from sorl.thumbnail.helpers import ThumbnailError
from sorl.thumbnail.helpers import toint


bgpos_pat = re.compile(r'^(?P<value>\d+)(?P<unit>%|px)$')
geometry_pat = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?$')


class ThumbnailParseError(ThumbnailError):
    pass


def parse_geometry(geometry, image_xy=None):
    """
    Parses a geometry string syntax and returns a (width, height) tuple
    """
    m = geometry_pat.match(geometry)
    def syntax_error():
        return ThumbnailParseError('Geometry does not have the correct '
                'syntax: %s' % geometry)
    if not m:
        raise syntax_error()
    x = m.group('x')
    y = m.group('y')
    if x is None and y is None:
        raise syntax_error()
    if x is not None:
        x = int(x)
    if y is not None:
        y = int(y)
    # calculate x or y proportionally if not set
    # but we need the image size for this
    if image_xy is not None:
        image_x, image_y = map(float, image_xy)
        if x is None:
            x = toint(image_x * y / image_y)
        elif y is None:
            y = toint(image_y * x / image_x)
    return x, y


def parse_crop(crop, image_xy, requested_xy):
    """
    Returns x, y offsets for cropping. The requested area should fit inside
    image but it works out anyway
    """
    def syntax_error():
        raise ThumbnailParseError('Unrecognized crop option: %s' % crop)
    ax_to_percent = {
        'left': '0%',
        'center': '50%',
        'right': '100%',
    }
    ay_to_percent = {
        'top': '0%',
        'center': '50%',
        'bottom': '100%',
    }
    crop_xy = crop.split(' ')
    if len(crop_xy) == 1:
        if crop in ax_to_percent:
            crop_x = ax_to_percent[crop]
            crop_y = '50%'
        elif crop in ay_to_percent:
            crop_y = ay_to_percent[crop]
            crop_x = '50%'
        else:
            crop_x, crop_y = crop, crop
    elif len(crop_xy) == 2:
        crop_x, crop_y = crop_xy
        crop_x = ax_to_percent.get(crop_x, crop_x)
        crop_y = ay_to_percent.get(crop_y, crop_y)
    else:
        syntax_error()

    def get_offset(crop, epsilon):
        m = bgpos_pat.match(crop)
        if not m:
            syntax_error()
        value = int(m.group('value')) # we only take ints in the regexp
        unit = m.group('unit')
        if unit == '%':
            value = epsilon * value / 100.0
        # return ∈ [0, epsilon]
        return int(max(0, min(value, epsilon)))

    offset_x = get_offset(crop_x, image_xy[0] - requested_xy[0])
    offset_y = get_offset(crop_y, image_xy[1] - requested_xy[1])
    return offset_x, offset_y

