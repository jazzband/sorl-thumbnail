from __future__ import division

import math
from cStringIO import StringIO
from sorl.thumbnail.engines.base import EngineBase

try:
    from PIL import Image, ImageFile, ImageDraw
except ImportError:
    import Image, ImageFile, ImageDraw


class Engine(EngineBase):
    def get_image(self, source):
        buf = StringIO(source.read())
        return Image.open(buf)

    def get_image_size(self, image):
        return image.size

    def is_valid_image(self, raw_data):
        buf = StringIO(raw_data)
        try:
            trial_image = Image.open(buf)
            trial_image.verify()
        except Exception:
            return False
        return True

    def _orientation(self, image):
        try:
            exif = image._getexif()
        except AttributeError:
            exif = None
        if exif:
            orientation = exif.get(0x0112)
            if orientation == 2:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                image = image.rotate(180)
            elif orientation == 4:
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            elif orientation == 5:
                image = image.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                image = image.rotate(-90)
            elif orientation == 7:
                image = image.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                image = image.rotate(90)
        return image

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            if image.mode == 'RGBA':
                return image # RGBA is just RGB + Alpha
            if image.mode == 'P' and 'transparency' in image.info:
                return image.convert('RGBA')
            return image.convert('RGB')
        if colorspace == 'GRAY':
            return image.convert('L')
        return image
        
    def _remove_border(self, image, image_width, image_height):
    
        image_entropy = self._get_image_entropy(image)
        
        borders = {
            'top' : lambda iy, dy, y: (dy, dy+y),
            'right' : lambda ix, dx, x: (ix-dx-x, ix-dx),
            'bottom' : lambda iy, dy, y: (iy-dy-y, iy-dy),
            'left': lambda ix, dx, x: (dx, dx+x),
        }
            
        offset = {'top':0, 'right':0, 'bottom':0, 'left':0,}
        
        for border in ['top', 'bottom']:
            # Don't remove too much, the image may just be plain
            while offset[border] < image_height/3.5:
              slice_size = min(image_width/20, 10)
              y_range = borders[border](image_height, offset[border], slice_size)
              section = image.crop((0, y_range[0], image_width, y_range[1]))
              # If this section is below the threshold; remove it
              if self._get_image_entropy(section) < 2.0:
                  offset[border] += slice_size
              else:
                  break
        
        for border in ['left', 'right']:
            while offset[border] < image_width/3.5:
              slice_size = min(image_height/20, 10)
              x_range = borders[border](image_width, offset[border], slice_size)
              section = image.crop((x_range[0], 0, x_range[1], image_height))
              if self._get_image_entropy(section) < 2.0:
                  offset[border] += slice_size
              else:
                  break
                  
        return image.crop((offset['left'], offset['top'], image_width-offset['right'], image_height-offset['bottom']))
    
    # Credit to chrisopherhan https://github.com/christopherhan/pycrop
    # This is just a slight rework of pycrops implimentation
    def _entropy_crop(self, image, geometry_width, geometry_height, image_width, image_height):
    
        geometry_ratio = geometry_width/geometry_height
    
        # The is proportionally wider than it should be
        while image_width/image_height > geometry_ratio:

            slice_width = max(image_width-geometry_width, 10)
            
            right = image.crop((image_width-slice_width, 0, image_width, image_height))
            left = image.crop((0, 0, slice_width, image_height))
        
            if self._get_image_entropy(left) < self._get_image_entropy(right):
                image = image.crop((slice_width, 0, image_width, image_height))
            else:
                image = image.crop((0, 0, image_height-slice_width, image_height))
                
            image_width -= slice_width
                
        # The image is proportionally taller than it should be
        while image_width/image_height < geometry_ratio:
          
            slice_height = min(image_height-geometry_height, 10)
            
            bottom = image.crop((0, image_height - slice_height, image_width, image_height))
            top = image.crop((0, 0, image_width, slice_height))

            if self._get_image_entropy(bottom) < self._get_image_entropy(top):
                image = image.crop((0, 0, image_width, image_height - slice_height))
            else:
                image = image.crop((0, slice_height, image_width, image_height))
                
            image_height -= slice_height
        
        return image   
        

    def _scale(self, image, width, height):
        return image.resize((width, height), resample=Image.ANTIALIAS)

    def _crop(self, image, width, height, x_offset, y_offset):
        return image.crop((x_offset, y_offset,
                           width + x_offset, height + y_offset))

    def _get_raw_data(self, image, format_, quality, progressive=False):
        ImageFile.MAXBLOCK = 1024 * 1024
        buf = StringIO()
        params = {
            'format': format_,
            'quality': quality,
            'optimize': 1,
        }
        if format_ == 'JPEG' and progressive:
            params['progressive'] = True
        try:
            image.save(buf, **params)
        except IOError:
            params.pop('optimize')
            image.save(buf, **params)
        raw_data = buf.getvalue()
        buf.close()
        return raw_data
        
    # calculate the entropy of an image
    def _get_image_entropy(self, image):
       hist = image.histogram()
       hist_size = sum(hist)
       hist = [float(h) / hist_size for h in hist]
       return -sum([p * math.log(p, 2) for p in hist if p != 0])
