from django import VERSION
from django.conf.urls.defaults import *
from django.conf import settings

if VERSION[0:2] < (1, 5):
    template_view = 'django.views.generic.simple.direct_to_template'
else:
    from django.views.generic.base import TemplateView
    class MyTemplateView(TemplateView):
        def get(self, request, *args, **kwargs):
            self.template_name = args[0] # get the template_name from the URL
            return super(MyTemplateView, self).get(request, *args, **kwargs)
    template_view = MyTemplateView.as_view()

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
        'show_indexes': True}
    ),
    (r'^(.*\.html)$', template_view),
)

