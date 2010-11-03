#coding=utf-8
import re
from sorl.thumbnail.helpers import ThumbnailError, toint


bgpos_pat = re.compile(r'^(?P<value>\d+)(?P<unit>%|px)$')
geometry_pat = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?$')


class ThumbnailParseError(ThumbnailError):
    pass


def parse_geometry(geometry, xy_image=None):
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
    if xy_image is not None:
        x_image, y_image = map(float, xy_image)
        if x is None:
            x = toint(x_image * y / y_image)
        elif y is None:
            y = toint(y_image * x / x_image)
    return x, y


def parse_crop(crop, xy_image, xy_window):
    """
    Returns x, y offsets for cropping. The window area should fit inside
    image but it works out anyway
    """
    def syntax_error():
        raise ThumbnailParseError('Unrecognized crop option: %s' % crop)
    x_alias_percent = {
        'left': '0%',
        'center': '50%',
        'right': '100%',
    }
    y_alias_percent = {
        'top': '0%',
        'center': '50%',
        'bottom': '100%',
    }
    xy_crop = crop.split(' ')
    if len(xy_crop) == 1:
        if crop in x_alias_percent:
            x_crop = x_alias_percent[crop]
            y_crop = '50%'
        elif crop in y_alias_percent:
            y_crop = y_alias_percent[crop]
            x_crop = '50%'
        else:
            x_crop, y_crop = crop, crop
    elif len(xy_crop) == 2:
        x_crop, y_crop = xy_crop
        x_crop = x_alias_percent.get(x_crop, x_crop)
        y_crop = y_alias_percent.get(y_crop, y_crop)
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

    offset_x = get_offset(x_crop, xy_image[0] - xy_window[0])
    offset_y = get_offset(y_crop, xy_image[1] - xy_window[1])
    return offset_x, offset_y

