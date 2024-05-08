from django.db import models
from django.contrib.auth.models import User


class Consumidor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='consumidor')

    def __str__(self):
        return self.user.username

class Productor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='productor')

    def __str__(self):
        return self.user.username
