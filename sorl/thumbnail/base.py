import os
from os import makedirs
from os.path import isfile, isdir, getmtime, dirname, splitext, getsize
from PIL import Image, ImageFilter
from methods import autocrop, resize_and_crop
from subprocess import Popen, PIPE
from tempfile import mkstemp


# Valid options for the Thumbnail class.
VALID_OPTIONS = ['crop', 'autocrop', 'upscale', 'bw', 'detail', 'sharpen']


class ThumbnailException(Exception):
    pass


class Thumbnail(object):
    def __init__(self, source, requested_size, opts=None, quality=85,
                 dest=None, imagemagick_path='/usr/bin/convert',
                 wvps_path='/usr/bin/wvPS'):
        # Converter paths
        self.imagemagick_path = imagemagick_path
        self.wvps_path = wvps_path
        # Absolute paths to files
        self.source = source
        self.dest = dest
        
        # Ensure the source file exists
        if not isfile(self.source):
            raise ThumbnailException('Source file does not exist')

        # Set the source type
        try:
            import magic
            m = magic.open(magic.MAGIC_NONE)
            m.load()
            ftype = m.file(self.source)
            if ftype.find('Microsoft Office Document') != -1:
                self.source_type = 'doc'
            elif ftype.find('PDF document') != -1:
                self.source_type = 'pdf'
            else:
                self.source_type = ftype
        except:
            self.source_type = splitext(self.source)[1].lower().replace('.', '')
        
        # Thumbnail settings
        self.requested_size = requested_size
        if not 0 < quality <= 100:
            raise TypeError('Thumbnail received invalid value for quality '
                            'argument: %s' % quality)
        self.quality = quality

        # Set Thumbnail opt(ion)s
        opts = opts or []
        # First we check that all options received are valid
        for opt in opts:
            if not opt in VALID_OPTIONS:
                raise TypeError('Thumbnail received an invalid option: %s'
                                % opt)
        # Then we populate the opts dict and the (sorted) opts list
        self.opts = {}
        self.opts_list = []
        for opt in VALID_OPTIONS:
            if opt in opts:
                self.opts[opt] = True
                self.opts_list.append(opt) # cheap sorted list with options
            else:
                self.opts[opt] = False
                
        if self.dest is not None:
            self.generate()

    def generate(self):
        """
        Generates the thumbnail if it doesn't exist or if the file date of the
        source file is newer than that of the thumbnail.
        """
        # Ensure dest(ination) attribute is set
        if not self.dest:
            raise ThumbnailException("No destination filename set.")

        if not isfile(self.dest) or \
           getmtime(self.source) > getmtime(self.dest):
            
            # Ensure the directory exists
            directory = dirname(self.dest)
            if not isdir(directory):
                makedirs(directory)
            
            self._do_generate()

    # data property is the image data of the (generated) thumbnail
    def _get_data(self):
        if not hasattr(self, '_data'):
            try:
                self._data = Image.open(self.dest)
            except IOError, detail:
                raise ThumbnailException(detail)
        return self._data
    def _set_data(self, im):
        self._data = im
    data = property(_get_data, _set_data)

    # source_data property is the image data from the source file
    def _get_source_data(self):
        if not hasattr(self, '_source_data'):
            if self.source_type == 'doc':
                self._convert_wvps(self.source)
            elif self.source_type == 'pdf':
                self._convert_imagemagick(self.source)
            else:
                self.source_data = self.source
        return self._source_data
    
    def _set_source_data(self, image):
        if isinstance(image, Image.Image):
            self._source_data = image
        else: 
            try:
                self._source_data = Image.open(image)
            except IOError, detail:
                raise ThumbnailException(detail)
    source_data = property(_get_source_data, _set_source_data)

    def _convert_wvps(self, filename):
        tmp = mkstemp('.ps')[1]
        try:
            p = Popen((self.wvps_path, filename, tmp), stdout=PIPE)
            p.wait()
        except OSError, detail:
            raise ThumbnailException('wvPS error: %s' % detail)
        self._convert_image_imagemagick(tmp)
        os.remove(tmp)

    def _convert_imagemagick(self, filename):
        tmp = mkstemp('.png')[1]
        if self.opts['crop']:
            x,y = [d*3 for d in self.requested_size]
        else:
            x,y = self.requested_size
        try:
            p = Popen((self.imagemagick_path, '-size', '%sx%s' % (x,y),
                '-antialias', '-colorspace', 'rgb', '-format', 'PNG32',
                '%s[0]' % filename, tmp), stdout=PIPE)
            p.wait()
        except OSError, detail:
            raise ThumbnailException('ImageMagick error: %s' % detail)
        self.source_data = tmp
        os.remove(tmp)
    
    def _do_generate(self):
        """
        Generates the thumbnail image.
        
        This a semi-private method so it isn't directly available to template
        authors if this object is passed to the template context.
        """
        im = self.source_data

        if self.opts['bw'] and im.mode != "L":
            im = im.convert("L")
        elif im.mode not in ("L", "RGB"):
            im = im.convert("RGB")

        if self.opts['autocrop']:
            im = autocrop(im)

        im = resize_and_crop(im, self.requested_size, self.opts['upscale'],
                             self.opts['crop'])

        if self.opts['detail']:
            im = im.filter(ImageFilter.DETAIL)

        if self.opts['sharpen']:
            im = im.filter(ImageFilter.SHARPEN)
        
        self.data = im
        try:
            im.save(self.dest, "JPEG", quality=self.quality, optimize=1)
        except IOError:
            # Try again, without optimization (the JPEG library can't optimize
            # an image which is larger than ImageFile.MAXBLOCK which is 64k by
            # default)
            try:
                im.save(self.dest, "JPEG", quality=self.quality)
            except IOError, detail:
                raise ThumbnailException(detail)

    # Some helpful methods

    def _dimension(self, axis):
        if self.dest is None:
            return None
        return self.data.size[axis]

    def width(self):
        return self._dimension(0)

    def height(self):
        return self._dimension(1)

    def _get_filesize(self):
        if self.dest is None:
            return None
        if not hasattr(self, '_filesize'):
            self._filesize = getsize(self.dest)
        return self._filesize
    filesize = property(_get_filesize)
   
    def _source_dimension(self, axis):
        if self.source_type in ['pdf', 'doc']:
            return None
        else:
            return self.source_data.size[axis]

    def source_width(self):
        return self._source_dimension(0)

    def source_height(self):
        return self._source_dimension(1)
    
    def _get_source_filesize(self):
        if not hasattr(self, '_source_filesize'):
            self._source_filesize = getsize(self.source)
        return self._source_filesize
    source_filesize = property(_get_source_filesize)
