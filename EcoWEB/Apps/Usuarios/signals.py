from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Consumidor, Productor, CustomUser

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Consumidor.objects.create(user=instance)
        print("Creado Usuario Consumidor")
    if instance.groups.filter(name='Productor').exists():
        Productor.objects.create(user=instance)
        print("Creado Usuario Productor")