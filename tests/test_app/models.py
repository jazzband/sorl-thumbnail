from django.db import models


class Item(models.Model):
    image = models.ImageField(upload_to=True)

