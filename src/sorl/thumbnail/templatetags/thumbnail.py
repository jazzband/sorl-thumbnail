import re
from django.template import Library, Node
from django.utils.encoding import force_unicode, smart_str
from sorl.thumbnail.conf import settings
from sorl.thumbnail.main import get_thumbnailfile


register = Library()
kw_pat = re.compile(r'^(?P<key>\w+)=(?P<value>.+)$')


@register.tag('thumbnail')
class ThumbnailNode(Node):
    def __init__(self, parser, token):
        def syntax_error():
            return TemplateSyntaxError('Syntax error.')
        bits = token.split_contents()
        if len(bits) < 5 or bits[-2] != 'as':
            raise syntax_error()
        self.input_file = parser.compile_filter(bits[1])
        self.geometry = parser_compile_filter(bits[2])
        self.kwargs = {}
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
        geometry_string = self.geometry.resolve(context)
        for k, v in self.kwargs.iteritems():
            self.kwargs[k] = v.resolve(context)
        thumbnail = get_thumbnailfile(input_file, geometry_string,
                                      **self.kwargs)
        context.push()
        context[self.as_var] = thumbnail
        output = self.nodelist.render(context)
        context.pop()
        return output

    def __repr__(self):
        return "<ThumbnailNode>"


