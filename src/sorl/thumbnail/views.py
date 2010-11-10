from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class


@cache_page(3600)
def thumbnail_dummy(request, width, height):
    width, height = int(width), int(height)
    engine = get_module_class(settings.THUMBNAIL_ENGINE)()
    image = engine.dummy_image(width, height)
    raw_data = engine._get_raw_data(image, format_='JPEG', quality=75)
    return HttpResponse(raw_data, mimetype='image/jpeg')

