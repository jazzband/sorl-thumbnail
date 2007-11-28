import os
from PIL import Image
from django.conf import settings
from django.utils.http import urlquote

class Thumbnail:

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

        self.filename_abs = os.path.join(settings.MEDIA_ROOT, self.filename)
        self.thumbnail = ""
        if os.path.isfile(self.filename_abs):
            self.set_thumbnail_filename()
            self.set_thumbnail()
        else:
            raise Exception("File does not exist.")

    def get_url(self):
        return "%s%s" % (settings.MEDIA_URL, "/".join(self.thumbnail.split(os.path.sep)))

    def set_thumbnail_filename(self):
        filehead, filetail = os.path.split(self.filename)
        basename, ext = os.path.splitext(filetail)
        thumbs_dir = os.path.join(settings.MEDIA_ROOT, filehead, self.subdir)
        if not os.path.isdir(thumbs_dir):
            os.mkdir(thumbs_dir)
                
        details = "%sx%s" % (self.size[0], self.size[1])
        if self.crop:
            details = "%s_%s" % (details, 'crop')
        if self.enlarge:
            details = "%s_%s" % (details, 'enlarge')
        self.thumbnail_filename = os.path.join(filehead, self.subdir, '%s%s_%s_q%s.jpg' % \
            (self.prefix, urlquote(basename), details, self.quality))
        self.thumbnail_filename_abs = os.path.join(settings.MEDIA_ROOT, self.thumbnail_filename)

    
    def set_thumbnail(self):
        if os.path.isfile(self.thumbnail_filename_abs):
            if os.path.getmtime(self.filename_abs) > os.path.getmtime(self.thumbnail_filename_abs):
                self.make_thumbnail()
            else:
                self.thumbnail = self.thumbnail_filename
        else:
            self.make_thumbnail()
            

    def make_thumbnail(self):
        im = Image.open(self.filename_abs)

        if im.mode not in ("L", "RGB"): 
            im = im.convert("RGB") 

        x, y   = [float(v) for v in im.size]
        xr, yr = [float(v) for v in self.size]

        if self.crop:
            r = max(xr/x, yr/y)
        else:
            r = min(xr/x, yr/y)
            
        if not self.enlarge:
            r = min(r,1)
        im = im.resize((int(x*r), int(y*r)), resample=Image.ANTIALIAS)
        
        if self.crop:
            x, y   = [float(v) for v in im.size]
            ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
            im = im.crop((int(ex), int(ey), int(x-ex), int(y-ey)))

        try:
            im.save(self.thumbnail_filename_abs, "JPEG", quality=self.quality, optimize=1)
        except:
            im.save(self.thumbnail_filename_abs, "JPEG", quality=self.quality)
        
        self.thumbnail = self.thumbnail_filename
