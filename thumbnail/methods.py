def autocrop(im):

    if im.mode != "RGB":
        im = im.convert("RGB")
    pix = im.load()
    
    x0, x1, y0, y1 = 0, im.size[0], 0, im.size[1]
    
    def pixel_is_white(pixel):
        for c in pixel:
            if c < 240: return False
        return True

    def col_is_white(x):
        for i in xrange(0,im.size[1]):
            if not pixel_is_white(pix[x,i]): return False
        return True
    
    def row_is_white(y):
        for i in xrange(0,im.size[0]):
            if not pixel_is_white(pix[i,y]): return False
        return True

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
