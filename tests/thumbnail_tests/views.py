from django.template import loader
from django.http import HttpResponse


def direct_to_template(request, template, mimetype=None, **kwargs):
    t = loader.get_template(template)
    return HttpResponse(t.render({'request': request}), content_type=mimetype)
