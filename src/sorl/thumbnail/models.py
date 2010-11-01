from django.core.cache import cache
from django.db import models
from django.db.models import signals
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_or_set_cache


def prefix_cache_key(key):
    return '%s%s' % (settings.THUMBNAIL_CACHE_PREFIX, key)


class CacheManager(models.Manager):
    def get(self, key):
        def get_from_db():
            sup = super(CacheManager, self)
            return sup.get_query_set().get(pk=key)
        cache_key = prefix_cache_key(key)
        return get_or_set_cache(cache_key, get_from_db)


class DBCacheBase(models.Model):
    key = models.CharField(max_length=32, primary_key=True)

    objects = models.Manager()
    cache = CacheManager()

    @property
    def cache_key(self):
        return prefix_cache_key(self.key)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        # XXX invalidate_cache
        super(DBCacheBase, self).save(**kwargs)
        # XXX update_cache

    def delete(self):
        # XXX invalidate_cache
        super(DBCacheBase, self).delete()

class Portrait(DBCacheBase):
    is_portrait = models.BooleanField()


class Thumbnail(DBCacheBase):
    source_name = models.CharField(max_length=1000)
    source_storage = models.CharField(max_length=200)
    geometry = models.CharField(max_length=11)
    options = models.CharField(max_length=1000)

    name = models.CharField(max_length=1000)
    url = models.CharField(max_length=1000)
    path = models.CharField(max_length=1000)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    # width, height aliases
    x = property(lambda self: self.width)
    y = property(lambda self: self.height)


def invalidate_cache(sender, instance, **kwargs):
    cache.delete(instance.cache_key)

def update_cache(sender, instance, **kwargs):
    cache.set(instance.cache_key, instance, settings.THUMBNAIL_CACHE_TIMEOUT)

signals.pre_save.connect(invalidate_cache, sender=Thumbnail)
signals.post_save.connect(update_cache, sender=Thumbnail)
signals.pre_delete.connect(invalidate_cache, sender=Thumbnail)

