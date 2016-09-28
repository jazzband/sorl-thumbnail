from django.conf.urls import url
from django.conf import settings
from django.views.static import serve

from .views import direct_to_template


urlpatterns = [
    url(r'^media/(?P<path>.+)$', serve,
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^(.*\.html)$', direct_to_template),
]
