try:
    from django.conf.urls import patterns
except ImportError:
    from django.conf.urls.defaults import patterns
from django.conf import settings

try:
    from django.views.generic.simple import direct_to_template
except ImportError:
    from views import direct_to_template

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
        'show_indexes': True}
    ),
    (r'^(.*\.html)$', direct_to_template),
)

