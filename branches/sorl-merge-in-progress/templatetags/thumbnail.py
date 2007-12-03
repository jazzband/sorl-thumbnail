import re
import os

from django import template
from django.conf import settings

from sorl.thumbnail.main import DjangoThumbnail
from sorl.thumbnail.base import OPTIONS

register = template.Library()
VALID_ARGS = ['quality', 'thumbs_dir']

class ThumbnailNode(template.Node):
    def __init__(self, source_var, context_name=None, opts=None,
                 extra_args=None, debug=False, thumbnail_class=DjangoThumbnail):
        self.context_name = context_name
        self.source_var = template.Variable(source_var)
        self.opts = opts or {}
        self.extra_args = dict([(k, template.Variable(v)) for k, v in 
                                (extra_args or {}).items()])
        self.debug = debug
        self.thumbnail_class = thumbnail_class
    def render(self, context):
        source_path = self.source_var.resolve(context)
        kwargs = dict([(k, v.resolve(context)) for k, v in
                       self.extra_args.items()])
        kwargs.update(self.opts)
        try:
            thumbnail = self.thumbnail_class(source_path, **kwargs)
        except:
            if self.debug:
                raise
            return ''
        if not self.context_name:
            return thumbnail
        context[self.context_name] = thumbnail
        return ''

class ThumbnailImgTagNode(template.Node):
    def __init__(self, thumbnail, attributes=None):
        self.thumbnail = template.Variable(thumbnail)
        self.attributes = dict([(k, template.Variable(v)) for k, v in
                                attributes.items()])
    def render(self, context):
        thumbnail = self.thumbnail.resolve(context)
        attributes = dict([(k, v.resolve(context)) for k, v in
                           self.attributes.items()])
        return thumbnail.img_tag(extra_attributes=attributes)

@register.tag
def thumbnail(parser, token):
    return get_thumbnail_node(token)

@register.tag
def thumbnail_debug(parser, token):
    return get_thumbnail_node(token, debug=True)

@register.tag
def thumbnail_imgtag(parser, token):
    """
    Output an HTML <img> tag for a DjangoThumbnail instance.

    Basic usage::

        {% thumbnail_imgtag thumb %}

    Pass HTML parameters like this:: 

        {% thumbnail_imgtag thumb class="preview" %}
        {% thumbnail_imgtag thumb alt=person.name %}
    """
    args = token.split_contents()
    if len(args) < 2:
        raise template.TemplateSyntaxError("'%s' tag requires at least one argument" % args[0])
    attributes = {}
    for arg in args[2:]:
        try:
            k, v = arg.split('=', 1)
        except ValueError:
            raise template.TemplateSyntaxError("'%s' received invalid argument format - expected 'attr=val' but got '%s'" % (args[0], arg))
        attributes[k] = v
    return ThumbnailImgTagNode(thumbnail=args[1], attributes=attributes)

re_dimensions = re.compile(r'(\d+)x(\d+)$')
def get_thumbnail_node(token, debug=False, thumbnail_class=DjangoThumbnail):
    """
    To just output the url to the thumbnail::

        {% thumbnail image_path 80x80 %}

    After the image path and dimensions, you can put any options::

        {% thumbnail image_path 80x80 quality=95 crop %}

    To put the DjangoThumbnail class on the context instead of just rendering
    the url, finish the tag with "as [context_var_name]"::

        {% thumbnail image_path 80x80 as thumb %}
        {{ thumb.thumbnail.size.0 }} x {{ thumb.thumbnail.size.1 }}
    """
    args = token.split_contents()
    if len(args) < 3:
        raise template.TemplateSyntaxError("'%s' tag requires at least two arguments" % args[0])
    source_var = args[1]
    opts = {}

    # Get the dimensions
    dimensions = re_dimensions.match(args[2])
    if not dimensions:
        raise template.TemplateSyntaxError("'%s' tag received invalid dimensions - expected something like 80x80 but got '%s'" % args[2])
    opts['size'] = [int(d) for d in dimensions.groups()]

    # Check to see if we're setting to a context variable.
    if len(args) >= 5 and args[-2] == 'as':
        context_name = args[-1]
        args = args[:-2]
    else:
        context_name = None

    # Check the rest of the options
    extra_args = {}
    for arg in args[3:]:
        k, v = parse_arg(arg)
        if v == True:
            if k not in OPTIONS:
                invalid_argument(args[0], arg)
            opts[str(k)] = v
        else:
            if k not in VALID_ARGS:
                invalid_argument(args[0], arg)
            extra_args[str(k)] = v

    return ThumbnailNode(source_var=source_var, context_name=context_name,
                         opts=opts, extra_args=extra_args, debug=debug,
                         thumbnail_class=thumbnail_class)

def parse_arg(arg):
    bits = arg.split('=', 1)
    if len(bits) < 2:
        return (arg, True)
    return bits

def invalid_argument(tag, arg):
    valid = ["'%s'" % o for o in OPTIONS] + ["'%s=...'" % a for a in VALID_ARGS]
    msg = "'%s' tag received invalid argument: '%s' (valid arguments are %s)"
    raise template.TemplateSyntaxError(msg % (tag, arg, ', '.join(valid)))
