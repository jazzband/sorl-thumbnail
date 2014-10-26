from django.db import models
from sorl.thumbnail import ImageField


class Item(models.Model):
    image = ImageField(upload_to=True)
