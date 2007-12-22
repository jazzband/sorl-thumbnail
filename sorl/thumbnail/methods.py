from PIL import Image, ImageFilter, ImageChops

def resize_and_crop(im, size, upscale, crop):
    
    x, y   = [float(v) for v in im.size]
    xr, yr = [float(v) for v in size]

    if crop:
        r = max(xr/x, yr/y)
    else:
        r = min(xr/x, yr/y)

    if r < 1.0 or (r > 1.0 and upscale):
        im = im.resize((int(x*r), int(y*r)), resample=Image.ANTIALIAS)

    if crop:
        x, y   = [float(v) for v in im.size]
        ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
        if ex or ey:
            im = im.crop((int(ex), int(ey), int(x-ex), int(y-ey)))
    
    return im


def autocrop(im):
    
    bw = im.convert("1")
    bw = bw.filter(ImageFilter.MedianFilter)

    # white bg
    bg = Image.new("1", im.size, 255)
    diff = ImageChops.difference(bw, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im
