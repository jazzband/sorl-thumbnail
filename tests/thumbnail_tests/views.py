from django.http import HttpResponse
from django.template import loader


def direct_to_template(request, template, mimetype=None, **kwargs):
    t = loader.get_template(template)
    return HttpResponse(t.render({'request': request}), content_type=mimetype)
