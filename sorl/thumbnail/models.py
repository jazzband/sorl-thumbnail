from django.db import models


class KVStore(models.Model):
    key = models.CharField(max_length=200, primary_key=True, db_column='key_field')
    value = models.TextField(db_column='value_field')

