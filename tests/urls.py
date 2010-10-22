from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
        'show_indexes': True}
    ),
    (r'(.*\.html)$', 'django.views.generic.simple.direct_to_template'),
)

