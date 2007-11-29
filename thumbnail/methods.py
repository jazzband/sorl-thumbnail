def autocrop(im):

    THRESHOLD_WHITE = 240
    ROW_RATIO = 0.8

    if im.mode != "RGB":
        im = im.convert("RGB")
    pix = im.load()
    
    x0, x1, y0, y1 = 0, im.size[0], 0, im.size[1]
    
    def pixel_is_white(pixel):
        for c in pixel:
            if c < THRESHOLD_WHITE: return 0
        return 1

    def col_is_white(x):
        s = 0.0
        for i in xrange(0,im.size[1]):
            s += pixel_is_white(pix[x,i])
        return s/float(im.size[1]) > ROW_RATIO
    
    def row_is_white(y):
        s = 0.0
        for i in xrange(0,im.size[0]):
            s += pixel_is_white(pix[i,y])
        return s/float(im.size[0]) > ROW_RATIO

    for i in xrange(0,im.size[0]):
        if not col_is_white(i):
            x0 = i
            break
        
    for i in xrange(0,im.size[1]):
        if not row_is_white(i):
            y0 = i
            break
    
    for i in xrange(im.size[0]-1,-1,-1):
        if not col_is_white(i):
            x1 = i+1
            break
        
    for i in xrange(im.size[1]-1,-1,-1):
        if not row_is_white(i):
            y1 = i+1
            break
    
    return im.crop((x0, y0, x1, y1))
