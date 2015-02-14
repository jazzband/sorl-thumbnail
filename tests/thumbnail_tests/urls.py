from django.conf.urls import patterns
from django.conf import settings


urlpatterns = patterns(
    '',
    (r'^media/(?P<path>.+)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    (r'^(.*\.html)$', 'tests.thumbnail_tests.views.direct_to_template'),
)
