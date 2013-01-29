#coding=utf-8
import re
from sorl.thumbnail.helpers import ThumbnailError, toint


bgpos_pat = re.compile(r'^(?P<value>\d+)(?P<unit>%|px)$')
geometry_pat = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?$')


class ThumbnailParseError(ThumbnailError):
    pass


def parse_geometry(geometry, ratio=None):
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
    # calculate x or y proportionally if not set but we need the image ratio
    # for this
    if ratio is not None:
        ratio = float(ratio)
        if x is None:
            x = toint(y * ratio)
        elif y is None:
            y = toint(x / ratio)
    return x, y


def parse_crop(crop, xy_image):
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
    xywh_crop = crop.split(' ')
    if len(xywh_crop) == 1:
        if crop in x_alias_percent:
            x_crop = x_alias_percent[crop]
            y_crop = '50%'
            w_crop = '100%'
            h_crop = '100%'

        elif crop in y_alias_percent:
            y_crop = y_alias_percent[crop]
            x_crop = '50%'
            w_crop = '100%'
            h_crop = '100%'

        else:
            x_crop, y_crop = crop, crop
            w_crop, h_crop = '100%', '100%'
            
    elif len(xywh_crop) == 2:
        x_crop, y_crop = xywh_crop
        x_crop = x_alias_percent.get(x_crop, x_crop)
        y_crop = y_alias_percent.get(y_crop, y_crop)
        w_crop, h_crop = '100%', '100%'
        
    elif len(xywh_crop) == 3:
        x_crop, y_crop = xywh_crop[0], xywh_crop[1]
        x_crop = x_alias_percent.get(x_crop, x_crop)
        y_crop = y_alias_percent.get(y_crop, y_crop)

        w = xywh_crop[2]
        if w in x_alias_percent:
            w_crop = x_alias_percent[w]
            h_crop = '100%'
            
        elif w in y_alias_percent:
            h_crop = y_alias_percent[w]
            w_crop = '100%'
            
        else:
            w_crop, h_crop = w, w
    
    elif len(xywh_crop) == 4:
        x_crop, y_crop = xywh_crop[0], xywh_crop[1]
        x_crop = x_alias_percent.get(x_crop, x_crop)
        y_crop = y_alias_percent.get(y_crop, y_crop)

        w_crop, h_crop = xywh_crop[2], xywh_crop[3]
        w_crop = x_alias_percent.get(w_crop, w_crop)
        h_crop = y_alias_percent.get(h_crop, h_crop)
    
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

    window_x = get_offset(w_crop, xy_image[0])
    window_y = get_offset(h_crop, xy_image[1])
    offset_x = get_offset(x_crop, xy_image[0] - window_x)
    offset_y = get_offset(y_crop, xy_image[1] - window_y)
    return offset_x, offset_y, window_x, window_y

