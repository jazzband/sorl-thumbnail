import os
from os.path import isfile, isdir, getmtime, dirname, splitext, getsize
from tempfile import mkstemp
from shutil import copyfile
from subprocess import Popen, PIPE

from PIL import Image, ImageFilter

from sorl.thumbnail import defaults
from sorl.thumbnail.processors import get_valid_options, dynamic_import


class ThumbnailException(Exception):
    pass


class Thumbnail(object):
    def __init__(self, source, requested_size, opts=None, quality=85,
                 dest=None, convert_path=defaults.CONVERT,
                 wvps_path=defaults.WVPS, processors=None):
        # Paths to external commands
        self.convert_path = convert_path
        self.wvps_path = wvps_path
        # Absolute paths to files
        self.source = source
        self.dest = dest

        # Thumbnail settings
        self.requested_size = requested_size
        if not 0 < quality <= 100:
            raise TypeError('Thumbnail received invalid value for quality '
                            'argument: %s' % quality)
        self.quality = quality

        # Processors
        if processors is None:
            processors = dynamic_import(defaults.PROCESSORS)
        self.processors = processors

        # Set Thumbnail opt(ion)s
        VALID_OPTIONS = get_valid_options(processors)
        opts = opts or []
        # Check that all options received are valid
        for opt in opts:
            if not opt in VALID_OPTIONS:
                raise TypeError('Thumbnail received an invalid option: %s'
                                % opt)
        self.opts = [opt for opt in VALID_OPTIONS if opt in opts]

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

        if not isinstance(self.dest, basestring):
            # We'll assume dest is a file-like instance if it exists but isn't
            # a string.
            self._do_generate()
        elif not isfile(self.dest) or (self.source_exists and
            getmtime(self.source) > getmtime(self.dest)):

            # Ensure the directory exists
            directory = dirname(self.dest)
            if not isdir(directory):
                os.makedirs(directory)

            self._do_generate()

    def _check_source_exists(self):
        """
        Ensure the source file exists. If source is not a string then it is
        assumed to be a file-like instance which "exists".
        """
        if not hasattr(self, '_source_exists'):
            self._source_exists = (self.source and
                                   (not isinstance(self.source, basestring) or
                                    isfile(self.source)))
        return self._source_exists
    source_exists = property(_check_source_exists)

    def _get_source_filetype(self):
        """
        Set the source filetype. First it tries to use magic and
        if import error it will just use the extension
        """
        if not hasattr(self, '_source_filetype'):
            if not isinstance(self.source, basestring):
                # Assuming a file-like object - we won't know it's type.
                return None
            try:
                import magic
            except ImportError:
                self._source_filetype = splitext(self.source)[1].lower().\
                   replace('.', '').replace('jpeg', 'jpg')
            else:
                m = magic.open(magic.MAGIC_NONE)
                m.load()
                ftype = m.file(self.source)
                if ftype.find('Microsoft Office Document') != -1:
                    self._source_filetype = 'doc'
                elif ftype.find('PDF document') != -1:
                    self._source_filetype = 'pdf'
                elif ftype.find('JPEG') != -1:
                    self._source_filetype = 'jpg'
                else:
                    self._source_filetype = ftype
        return self._source_filetype
    source_filetype = property(_get_source_filetype)

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
            if not self.source_exists:
                raise ThumbnailException("Source file: '%s' does not exist." %
                                         self.source)
            if self.source_filetype == 'doc':
                self._convert_wvps(self.source)
            elif self.source_filetype == 'pdf':
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
                raise ThumbnailException("%s: %s" % (detail, image))
    source_data = property(_get_source_data, _set_source_data)

    def _convert_wvps(self, filename):
        tmp = mkstemp('.ps')[1]
        try:
            p = Popen((self.wvps_path, filename, tmp), stdout=PIPE)
            p.wait()
        except OSError, detail:
            os.remove(tmp)
            raise ThumbnailException('wvPS error: %s' % detail)
        self._convert_imagemagick(tmp)
        os.remove(tmp)

    def _convert_imagemagick(self, filename):
        tmp = mkstemp('.png')[1]
        if 'crop' in self.opts or 'autocrop' in self.opts:
            x,y = [d*3 for d in self.requested_size]
        else:
            x,y = self.requested_size
        try:
            p = Popen((self.convert_path, '-size', '%sx%s' % (x,y),
                '-antialias', '-colorspace', 'rgb', '-format', 'PNG24',
                '%s[0]' % filename, tmp), stdout=PIPE)
            p.wait()
        except OSError, detail:
            os.remove(tmp)
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

        for processor in self.processors:
            im = processor(im, self.requested_size, self.opts)

        self.data = im

        if self.source_data == self.data and self.source_filetype == 'jpg':
            copyfile(self.source, self.dest)
        else:
            try:
                im.save(self.dest, "JPEG", quality=self.quality, optimize=1)
            except IOError:
                # Try again, without optimization (the JPEG library can't
                # optimize an image which is larger than ImageFile.MAXBLOCK
                # which is 64k by default)
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
        if self.source_filetype in ['pdf', 'doc']:
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
