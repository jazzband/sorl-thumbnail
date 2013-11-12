import django

__all__ = ['json']

if django.VERSION <= (1, 5):
    from django.utils import simplejson as json
else:
    import json
