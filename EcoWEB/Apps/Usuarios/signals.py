from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Consumidor, Productor

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Consumidor.objects.create(user=instance)
    if instance.groups.filter(name='Productor').exists():
        Productor.objects.create(user=instance)
