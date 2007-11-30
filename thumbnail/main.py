import os
from PIL import Image, ImageFilter
from django.conf import settings
from django.utils.encoding import iri_to_uri
from sorl.thumbnail.methods import autocrop


OPTIONS = ['crop', 'autocrop', 'upscale', 'bw', 'detail', 'sharpen']

class Thumbnail:

    def __init__(self, filename='', prefix='', subdir='_thumbs', quality=85,\
        filename_encoding='utf-8',size=(80.80), options=[]):
        
        self.filename_abs = os.path.join(settings.MEDIA_ROOT, filename)\
            .encode(filename_encoding)
        if not os.path.isfile(self.filename_abs):
            raise ThumbnailException("File does not exist.")

        self.filename = filename
        self.prefix   = prefix
        self.subdir   = subdir
        self.size     = size

        #invalid quality setting will just reset to default
        if quality > 1 and quality < 100:
            self.quality = quality
        else:
            self.quality = 85

        #invalid options silently ignored
        for o in OPTIONS:
            if o in options:
                setattr(self, o, True)
            else:
                setattr(self, o, False)
                
        self.filename_encoding = filename_encoding
        self.set_thumbnail_filename()

        if os.path.isfile(self.thumbnail_filename_abs):
            if os.path.getmtime(self.filename_abs) > os.path.getmtime(self.thumbnail_filename_abs):
                self.make_thumbnail()
        else:
            self.make_thumbnail()


    def __unicode__(self):
        return self.thumbnail_filename
    
   
    def get_url(self):
        return iri_to_uri("%s%s" % (settings.MEDIA_URL,\
            "/".join(self.thumbnail_filename.split(os.path.sep))))


    def set_thumbnail_filename(self):
        filehead, filetail = os.path.split(self.filename)
        basename, ext = os.path.splitext(filetail)
        thumbs_dir = os.path.join(settings.MEDIA_ROOT, filehead, self.subdir)
        if not os.path.isdir(thumbs_dir):
            os.mkdir(thumbs_dir)
        
        name_list = [basename, "%sx%s" % self.size]
        for o in OPTIONS:
            if getattr(self, o):
                name_list.append(o)
        name_list.append("q%s" % self.quality)

        self.thumbnail_filename = \
            os.path.join(filehead, self.subdir, '%s%s.jpg' % (self.prefix, "_".join(name_list)))
        self.thumbnail_filename_abs = os.path.join(settings.MEDIA_ROOT, self.thumbnail_filename)\
            .encode(self.filename_encoding)

    
    def make_thumbnail(self):
        try:
            im = Image.open(self.filename_abs)
        except IOError, detail:
            raise ThumbnailException(detail)

        if self.bw or im.mode not in ("L", "RGB"):
            if self.bw:
                im = im.convert("L")
            else:
                im = im.convert("RGB")
        
        if self.autocrop:
            im = autocrop(im)
        
        x, y   = [float(v) for v in im.size]
        xr, yr = [float(v) for v in self.size]

        if self.crop:
            r = max(xr/x, yr/y)
        else:
            r = min(xr/x, yr/y)
            
        if not self.upscale:
            r = min(r,1)
        im = im.resize((int(x*r), int(y*r)), resample=Image.ANTIALIAS)
        
        if self.crop:
            x, y   = [float(v) for v in im.size]
            ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
            im = im.crop((int(ex), int(ey), int(x-ex), int(y-ey)))

        if self.detail:
            im = im.filter(ImageFilter.DETAIL)
        if self.sharpen:
            im = im.filter(ImageFilter.SHARPEN)
        
        try:
            im.save(self.thumbnail_filename_abs, "JPEG", quality=self.quality, optimize=1)
        except:
            try:
                im.save(self.thumbnail_filename_abs, "JPEG", quality=self.quality)
            except IOError, detail:
                raise ThumbnailException(detail)

class ThumbnailException(Exception):
    pass
