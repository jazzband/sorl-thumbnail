from django.core.cache import cache
from django.db import models
from django.db.models import signals
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_unique_key


class ThumbnailDataManager(models.Manager):
    def get(self, source_name, source_storage, options):
        cache_key = get_unique_key(source_name, source_storage, options)
        data = cache.get(cache_key)
        if not data:
            obj = self.get_query_set.get(source_name=source_name,
                                         source_storage=source_storage,
                                         options=options)
            data = obj.__dict__
            cache.set(cache_key, data, settings.THUMBNAIL_CACHE_TIMEOUT)
        return data

class Thumbnail(models.Model):
    source_name = models.CharField(max_length=1000, db_index=True)
    source_storage = models.CharField(max_length=200, db_index=True)
    name = models.CharField(max_length=1000)
    url = models.CharField(max_length=1000, unique=True)
    path = models.CharField(max_length=1000)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    options = models.CharField(max_length=1000, db_index=True)
    size = models.PositiveIntegerField()

    data = ThumbnailDataManager()

    @property
    def cache_key(self):
        return get_unique_key(self.source_name, self.source_storage, self.options)

    class Meta:
        unique_together = (('source_name', 'source_storage', 'options'),)


def invalidate_cache(sender, instance, **kwargs):
    cache.delete(instance.cache_key)

def update_cache(sender, instance, **kwargs):
    data = instance.__dict__
    cache.set(instance.cache_key, data, settings.THUMBNAIL_CACHE_TIMEOUT)

signals.pre_save.connect(invalidate_cache, sender=Thumbnail)
signals.post_save.connect(update_cache, sender=Thumbnail)
signals.pre_delete.connect(invalidate_cache, sender=Thumbnail)

