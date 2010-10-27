from django.utils.encoding import smart_str, DEFAULT_LOCALE_ENCODING
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import ThumbnailError
from sorl.thumbnail.engines.base import ThumbnailEngineBase
from sorl.thumbnail.parsers import parse_geometry, parse_crop


class ThumbnailEngine(ThumbnailEngineBase):
    def resize(self, geometry, options):
        crop = options['crop']
        upscale = options['upscale']
        resize_option = '-resize %s' % geometry
        requested_xy = parse_geometry(geometry)
        crop_option = ''
        if not upscale:
            resize_option += '>' # this is probably incomplete
        # both x and y need to be set or us to crop
        if crop and None not in requested_xy:
            resize_option += '^'
            if crop is not 'noop':
                offset_x, offset_y = parse_crop(crop)[:2]
                crop_option = '-crop %s+%s+%s' % (geometry, offset_x, offset_y)
        return [resize_option, crop_option]

    def colorspace(self, options):
        return ['-colorspace %s' % options['colorspace']]

    def create(self, source, geometry, options, thumbnail):
        args = [settings.THUMBNAIL_CONVERT]
        args.extend(self.colorspace(options))
        args.extend(self.resize(geometry, options))
        self.write(args, options, thumbnail)

    def write(self, args, options, thumbnail):
        args.append('-quality %s' % options['quality'])
        print args
        #cmd = smart_str(cmd)
        #args.insert(0, cmd)
        #p = Popen(args, stderr=PIPE, stdout=PIPE)
        #retcode = p.wait()
        #if retcode != 0:
        #    raise ExecuteError(p.stderr.read().decode(DEFAULT_LOCALE_ENCODING))
        #return p.stdout.read().decode(DEFAULT_LOCALE_ENCODING)
        #    print args


