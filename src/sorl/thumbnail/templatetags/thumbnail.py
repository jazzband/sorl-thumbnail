import re
from django.core.cache import cache
from django.template import Library, Node, NodeList, TemplateSyntaxError
from django.utils.encoding import smart_str
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_thumbnail, mkhash, get_or_set_cache
from sorl.thumbnail.storage import SuperImage


register = Library()


kw_pat = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')


@register.tag('thumbnail')
class ThumbnailNode(Node):
    child_nodelists = ('nodelist_file', 'nodelist_empty')

    def __init__(self, parser, token):
        def syntax_error():
            raise TemplateSyntaxError('Syntax error.')
        bits = token.split_contents()
        if len(bits) < 5 or bits[-2] != 'as':
            syntax_error()
        self.file_ = parser.compile_filter(bits[1])
        self.geometry = parser.compile_filter(bits[2])
        self.options = {}
        for bit in bits[3:-2]:
            m = kw_pat.match(bit)
            if not m:
                syntax_error()
            key = smart_str(m.group('key'))
            value = parser.compile_filter(m.group('value'))
            self.options[key] = value
        self.as_var = bits[-1]
        self.nodelist_file = parser.parse(('empty', 'endthumbnail',))
        if parser.next_token().contents == 'empty':
            self.nodelist_empty = parser.parse(('endthumbnail',))
            parser.delete_first_token()
        else:
            self.nodelist_empty = NodeList()

    def render(self, context):
        try:
            return self._render(context)
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
        if not file_:
            return self.nodelist_empty.render(context)
        context.push()
        thumbnail = get_thumbnail(file_, geometry, **options)
        context[self.as_var] = thumbnail
        output = self.nodelist_file.render(context)
        context.pop()
        return output

    def __repr__(self):
        return "<ThumbnailNode>"

    def __iter__(self):
        for node in self.nodelist_file:
            yield node
        for node in self.nodelist_empty:
            yield node


@register.filter
def is_portrait(file_):
    """
    A very handy filter to determine if an image is portrait or landscape.
    Caching is used since this operation is not free.
    """
    image = SuperImage(file_)
    key = '%sportrait-%s' % (settings.THUMBNAIL_CACHE_PREFIX,
                             mkhash(image.name, image.storage_path))
    return get_or_set_cache(key, image.is_portrait)

