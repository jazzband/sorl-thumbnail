import re
from abc import ABCMeta, abstractmethod, abstractproperty
from django.core.cache import cache
from django.template import Library, Node, NodeList, TemplateSyntaxError
from django.utils.encoding import smart_str
from functools import wraps
from sorl.thumbnail.conf import settings
from sorl.thumbnail.storage import ImageFile
from sorl.thumbnail.helpers import get_module_class
from sorl.thumbnail.parsers import parse_geometry


register = Library()


kw_pat = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')


def safe_filter(error_output=''):
    """
    A safe filter decorator only raising errors when ``THUMBNAIL_DEBUG`` is
    ``True`` otherwise returning ``error_output``.
    """
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception:
                if settings.THUMBNAIL_DEBUG:
                    raise
                return error_output
        return wrapper
    return inner


class ThumbnailNodeBase(Node):
    """
    Renders safely and has a simple backend attribute.
    """
    __metaclass__ = ABCMeta

    error_output = ''

    @property
    def backend(self):
        if not hasattr(self, '_backend'):
            self._backend = get_module_class(settings.THUMBNAIL_BACKEND)()
        return self._backend

    def render(self, context):
        try:
            return self._render(context)
        except Exception:
            if settings.THUMBNAIL_DEBUG:
                raise
            return self.error_output

    @abstractmethod
    def _render(self, context):
        raise NotImplemented()


@register.tag('thumbnail')
class ThumbnailNode(ThumbnailNodeBase):
    child_nodelists = ('nodelist_file', 'nodelist_empty')

    def __init__(self, parser, token):
        bits = token.split_contents()
        if len(bits) < 5 or bits[-2] != 'as':
            raise TemplateSyntaxError('Syntax error.')
        self.file_ = parser.compile_filter(bits[1])
        self.geometry = parser.compile_filter(bits[2])
        self.options = {}
        for bit in bits[3:-2]:
            m = kw_pat.match(bit)
            if not m:
                raise TemplateSyntaxError('Syntax error.')
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

    def _render(self, context):
        file_ = self.file_.resolve(context)
        geometry = self.geometry.resolve(context)
        options = {}
        for key, value in self.options.iteritems():
            options[key] = value.resolve(context)
        if not file_:
            return self.nodelist_empty.render(context)
        context.push()
        thumbnail = self.backend.get_thumbnail(file_, geometry, **options)
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


@safe_filter(error_output='auto')
@register.filter
def is_portrait(file_):
    """
    A very handy filter to determine if an image is portrait or landscape.
    """
    image_file = ImageFile(file_)
    backend = get_module_class(settings.THUMBNAIL_BACKEND)()
    if not backend.store_get(image_file):
        image_file = backend.store_set(image_file)
    return image_file.is_portrait()


@safe_filter(error_output=False)
@register.filter
def margin(file_, geometry_string):
    """
    Returns the calculated margin for an image and geometry
    """
    margin = [0, 0, 0, 0]
    image_file = ImageFile(file_)
    backend = get_module_class(settings.THUMBNAIL_BACKEND)()
    if not backend.store_get(image_file):
        image_file = backend.store_set(image_file)
    x, y = parse_geometry(geometry_string)
    if x is not None:
        ex = x - image_file.x
        margin[3] = ex / 2
        margin[1] = ex / 2
        if ex % 2:
            margin[1] += 1
    if y is not None:
        ey = y - image_file.y
        margin[0] = ey / 2
        margin[2] = ey / 2
        if ey % 2:
            margin[2] += 1
    return ' '.join([ '%spx' % n for n in margin ])

