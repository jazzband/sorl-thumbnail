from django.utils.encoding import smart_str, DEFAULT_LOCALE_ENCODING
from sorl.thumbnail.helpers import ThumbnailError
from sorl.thumbnail.engines.base import ThumbnailEngineBase
from sorl.thumbnail.parsers import parse_geometry, parse_crop


class ThumbnailEngine(ThumbnailEngineBase):
    def resize(self, geometry, options):
        crop = options['crop'])
        upscale = options['upscale']
        resize_option = '-resize %s' % geometry
        crop_option = ''
        if not upscale:
            resize_option += '>' # this is probably incomplete
        if crop:
            resize_option += '^'
            if crop is not 'noop':
                offset_x, offset_y = parse_crop(crop)[:2]
                crop_option = '-crop %s+%s+%s' (geometry, offset_x, offset_y)
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



class ExecuteError(ThumbnailError):
    pass


def execute(cmd, args):
    if isinstance(args, basestring):
        args = smart_str(args)
        args = shlex.split(args)
    else:
        args = map(smart_str, args)
    cmd = smart_str(cmd)
    args.insert(0, cmd)
    p = Popen(args, stderr=PIPE, stdout=PIPE)
    retcode = p.wait()
    if retcode != 0:
        raise ExecuteError(p.stderr.read().decode(DEFAULT_LOCALE_ENCODING))
    return p.stdout.read().decode(DEFAULT_LOCALE_ENCODING)
