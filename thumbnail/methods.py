def autocrop(im):

    WHITE_RATIO = 0.95

    bw = im.convert("1")
    pix = bw.load()
    
    x0, x1, y0, y1 = 0, im.size[0], 0, im.size[1]
    
    def col_is_white(x):
        s = 0.0
        for i in xrange(0,im.size[1]):
            s += pix[x,i]/255
        return s/float(im.size[1]) > WHITE_RATIO
    
    def row_is_white(y):
        s = 0.0
        for i in xrange(0,im.size[0]):
            s += pix[i,y]/255
        return s/float(im.size[0]) > WHITE_RATIO

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
