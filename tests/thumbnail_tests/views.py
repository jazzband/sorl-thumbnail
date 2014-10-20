from django.template import loader, RequestContext
from django.http import HttpResponse


def direct_to_template(request, template, mimetype=None, **kwargs):
    c = RequestContext(request, {})
    t = loader.get_template(template)
    return HttpResponse(t.render(c), content_type=mimetype)
