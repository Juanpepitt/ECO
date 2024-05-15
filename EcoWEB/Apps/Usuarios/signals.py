# from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Consumidor, Productor, CustomUser
# from firebase_admin import auth, exceptions

# @receiver(post_save, sender=User)
# def create_or_update_firebase_user(sender, instance, created, **kwargs):
#     try:
#         if created:
#             user_record = auth.create_user(
#                 uid=str(instance.id),
#                 email=instance.email,
#                 display_name=instance.username,
#                 email_verified=True,
#             )
#             print(f'Successfully created new user: {user_record.uid}')
#         else:
#             user_record = auth.update_user(
#                 uid=str(instance.id),
#                 email=instance.email,
#                 display_name=instance.username,
#             )
#             print(f'Successfully updated user: {user_record.uid}')
#     except exceptions.FirebaseError as e:
#         print(f'Error updating Firebase user: {e}')



# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Consumidor.objects.create(user=instance)
#         print("Creado Usuario Consumidor")
#     if instance.groups.filter(name='Productor').exists():
#         Productor.objects.create(user=instance)
#         print("Creado Usuario Productor")