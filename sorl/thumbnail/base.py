from os import makedirs
from os.path import isfile, isdir, getmtime, dirname, splitext, getsize
from PIL import Image, ImageFilter
from methods import autocrop, resize_and_crop


# Valid options for the Thumbnail class.
VALID_OPTIONS = ['crop', 'autocrop', 'upscale', 'bw', 'detail', 'sharpen']


class ThumbnailException(Exception):
    pass


class Thumbnail(object):
    def __init__(self, source, requested_size, opts=None, quality=85,
                 dest=None):
        # Absolute paths to files
        self.source = source
        self.dest = dest
        
        # Ensure the source file exists
        if not isfile(self.source):
            raise ThumbnailException('Source file does not exist')
        
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
            #basename, ext = splitext(self.source)
            #ext = ext.lower()
            #if ext == '.doc':
            #    # try and use wvPS else just fetch an icon
            #    pass
            #elif ext == '.pdf':
            #    # do imagemagick stuff if possible
            #    try:
            #        from PythonMagick import *
            #        from cStringIO import StringIO
            #    except:
            #        # just fetch a pdf icon
            #        pass
            #else:
            try:
                self._source_data = Image.open(self.source)
            except IOError, detail:
                raise ThumbnailException(detail)
        return self._source_data
    def _set_source_data(self, im):
        self._source_data = im
    source_data = property(_get_source_data, _set_source_data)

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

    def width(self):
        if self.dest is None:
            return None
        return self.data.size[0]

    def height(self):
        if self.dest is None:
            return None
        return self.data.size[1]

    def filesize(self):
        if self.dest is None:
            return None
        return self.byteprefix(getsize(self.dest))

    def source_width(self):
        return self.source_data.size[0]

    def source_height(self):
        return self.source_data.size[1]
    
    def source_filesize(self):
        return self.byteprefix(getsize(self.source))
    
    def byteprefix(self, b):
        """
        Given an integer as number of bytes it returns a dict of
        Bytes, Kilobytes, Kibibytes, Megabytes and Mebibytes.
        """
        kb  = int(round(float(b)/1000.0,0))
        kib = int(round(float(b)/1024.0,0))
        mb  = round(float(b)/1000000.0,1)
        mib = round(float(b)/1048576.0,1)
        return {'b': b, 'kb': kb, 'kib': kib, 'mb': mb, 'mib': mib}
