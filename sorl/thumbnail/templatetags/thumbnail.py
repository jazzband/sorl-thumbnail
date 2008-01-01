import re
from django.template import Library, Node, Variable, VariableDoesNotExist, TemplateSyntaxError
from django.conf import settings
from sorl.thumbnail.base import VALID_OPTIONS
from sorl.thumbnail.main import DjangoThumbnail
from sorl.thumbnail.utils import get_thumbnail_setting

register = Library()

size_pat = re.compile(r'(\d+)x(\d+)$')
quality_pat = re.compile(r'quality=([1-9]\d?|100)$')


class ThumbnailNode(Node):

    def __init__(self, source_var, requested_size, opts=None,
                 context_name=None, **kwargs):
        self.source_var = Variable(source_var)
        self.requested_size = requested_size
        self.opts = opts
        self.context_name = context_name
        self.kwargs = kwargs
    
    def render(self, context):
        thumbnail = ''
        try:
            relative_source = self.source_var.resolve(context)
            thumbnail = DjangoThumbnail(relative_source, self.requested_size,
                                        opts=self.opts, **self.kwargs)
        except VariableDoesNotExist:
            if get_thumbnail_setting('DEBUG'):
                raise VariableDoesNotExist("Variable %s does not exist." %
                                           self.source_var)
        except:
            if get_thumbnail_setting('DEBUG'):
                raise
            
        if self.context_name is None:
            return thumbnail
        context[self.context_name] = thumbnail
        return ''


def thumbnail(parser, token):
    """
    To just output the absolute url to the thumbnail::

        {% thumbnail image 80x80 %}

    After the image path and dimensions, you can put any options::

        {% thumbnail image 80x80 quality=95,crop %}

    To put the DjangoThumbnail class on the context instead of just rendering
    the absolute url, finish the tag with "as [context_var_name]"::

        {% thumbnail image 80x80 as thumb %}
        {{ thumb.width }} x {{ thumb.height }}
    """
    args = token.split_contents()
    tag = args[0]
    # Check to see if we're setting to a context variable.
    if len(args) in (5, 6) and args[-2] == 'as':
        context_name = args[-1]
        args = args[:-2]
    else:
        context_name = None

    if len(args) not in (3, 4):
        raise TemplateSyntaxError("Invalid syntax. Expected "
            "'{%% %s source size [options] %%}' or "
            "'{%% %s source size [options] as variable %%}'" % (tag, tag)) 

    # Get the source image path.
    source_var = args[1]

    # Get the requested size.
    if args[2][0] in [ "'", '"'] and args[2][0] == args[2][-1]:
        args[2] = args[2][1:-1]
    m = size_pat.match(args[2])
    if not m:
        raise TemplateSyntaxError("'%s' tag received invalid requested size. "
            "Expected something like 80x80 but got: '%s'" % (tag, args[2]))
    requested_size = (int(m.group(1)), int(m.group(2)))

    # Get the options.
    if len(args) == 4:
        args_list = args[3].split(',')
    else:
        args_list = []

    # Check the options.
    opts = []
    kwargs = {} # key,values here override settings and defaults
    for arg in args_list:
        if arg in VALID_OPTIONS:
            opts.append(arg)
        else:
            m = quality_pat.match(arg)
            if not m:
                raise TemplateSyntaxError(
                    "'%s' tag received a bad argument: '%s'" % (tag, arg))
            kwargs['quality'] = int(m.group(1))
    return ThumbnailNode(source_var, requested_size, opts=opts,
                         context_name=context_name, **kwargs)


register.tag(thumbnail)
