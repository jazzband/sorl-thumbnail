from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.cache import cache_page
from sorl.thumbnail.conf import settings
from sorl.thumbnail import default


@cache_page(3600)
def thumbnail_dummy(request, width, height):
    if not request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
        return HttpResponseForbidden()
    width, height = int(width), int(height)
    image = default.engine.dummy_image(width, height)
    raw_data = default.engine._get_raw_data(image, format_='JPEG', quality=75)
    return HttpResponse(raw_data, mimetype='image/jpeg')

