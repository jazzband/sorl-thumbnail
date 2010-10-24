import re
from django.template import Library, Node, TemplateSyntaxError
from django.utils.encoding import smart_str
from sorl.thumbnail.conf import settings
from sorl.thumbnail.base import get_thumbnailfile


register = Library()
kw_pat = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')


@register.tag('thumbnail')
class ThumbnailNode(Node):
    def __init__(self, parser, token):
        def syntax_error():
            return TemplateSyntaxError('Syntax error.')
        bits = token.split_contents()
        if len(bits) < 5 or bits[-2] != 'as':
            raise syntax_error()
        self.input_file = parser.compile_filter(bits[1])
        self.portrait = parser.compile_filter(bits[2])
        self.kwargs = {}
        if len(bits) > 5 and not kw_pat.match(bits[3]):
            self.landscape = parser.compile_filter(bits.pop(3))
        else:
            self.landscape = None
        for bit in bits[2:-3]:
            m = kw_pat.match(bit)
            if not m:
                raise syntax_error()
            key = smart_str(m.group('key'))
            value = parser.compile_filter(m.group('value'))
            self.kwargs[key] = value
        self.as_var = bits[-1]
        self.nodelist = parser.parse(('endthumbnail',))
        parser.delete_first_token()

    def render(self, context):
        try:
            self._render(context)
        except Exception:
            if settings.THUMBNAIL_DEBUG:
                raise
            return settings.THUMBNAIL_ERROR

    def _render(self, context):
        input_file = self.input_file.resolve(context)
        portrait_string = self.portrait.resolve(context)
        if self.landscape is not None:
            landscape_string = self.landscape.resolve(context)
        else:
            landscape_string = None
        for k, v in self.kwargs.iteritems():
            self.kwargs[k] = v.resolve(context)
        thumbnail = get_thumbnailfile(input_file, portrait_string,
                                      landscape_string, **self.kwargs)
        context.push()
        context[self.as_var] = thumbnail
        output = self.nodelist.render(context)
        context.pop()
        return output

    def __repr__(self):
        return "<ThumbnailNode>"


