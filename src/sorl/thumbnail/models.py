from django.db import models


class KeyStore(models.Model):
    key = models.CharFIeld(max_length=200, primary_key=True)
    value = models.TextField()

