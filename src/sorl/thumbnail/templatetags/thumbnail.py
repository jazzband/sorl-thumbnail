import re
from django.template import Library, Node, TemplateSyntaxError
from django.utils.encoding import smart_str
from sorl.thumbnail.helpers import get_thumbnail
from sorl.thumbnail.conf import settings


register = Library()


kw_pat = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')
integer_pat = re.compile(r'^\d+$')
bool_pat = re.compile(r'^(True|False)$')


@register.tag('thumbnail')
class ThumbnailNode(Node):
    def __init__(self, parser, token):
        def syntax_error():
            return TemplateSyntaxError('Syntax error.')
        bits = token.split_contents()
        if len(bits) < 5 or bits[-2] != 'as':
            raise syntax_error()
        self.file_ = parser.compile_filter(bits[1])
        self.geometry = parser.compile_filter(bits[2])
        self.options = {}
        for bit in bits[2:-3]:
            m = kw_pat.match(bit)
            if not m:
                raise syntax_error()
            key = smart_str(m.group('key'))
            value = parser.compile_filter(m.group('value'))
            self.options[key] = value
        self.as_var = bits[-1]
        self.nodelist = parser.parse(('endthumbnail',))
        parser.delete_first_token()

    def render(self, context):
        try:
            self._render(context)
        except Exception:
            if settings.THUMBNAIL_DEBUG:
                raise
            context[self.as_var] = None # reset in case it was set in a loop
            return settings.THUMBNAIL_ERROR

    def _render(self, context):
        file_ = self.file_.resolve(context)
        geometry = self.geometry.resolve(context)
        options = {}
        for key, value in self.options.iteritems():
            options[key] = value.resolve(context)
        thumbnail = get_thumbnail(file_, geometry, **options)
        context.push()
        context[self.as_var] = thumbnail
        output = self.nodelist.render(context)
        context.pop()
        return output

    def __repr__(self):
        return "<ThumbnailNode>"

