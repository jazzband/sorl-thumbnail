from django.conf.urls.defaults import *
from sorl.thumbnail.conf import settings


if settings.THUMBNAIL_DUMMY:
    urlpatterns = patterns('',
        url('^thumbnail-dummy/(\d+)x(\d+)/$',
            'sorl.thumbnail.views.thumbnail_dummy',
            name='thumbnail_dummy',
        ),
    )
else:
    urlpatterns = patterns('',)

