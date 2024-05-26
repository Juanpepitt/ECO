# from allauth.account.adapter import DefaultAccountAdapter
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from .models import Consumidor

# class CustomAccountAdapter(DefaultAccountAdapter):
#     def save_user(self, request, user, form, commit=True):
#         user = super().save_user(request, user, form, commit=False)
#         user.username = user.email  # Asegurarse de que el username sea igual al email
#         if commit:
#             user.save()
#         return user

# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
#     def populate_user(self, request, sociallogin, data):
#         user = sociallogin.user
#         user.email = data.get('email', '')
#         user.username = user.email  # Asegurarse de que el username sea igual al email
#         user.nombre = data.get('first_name', '')
#         user.apellidos = data.get('last_name', '')
#         return user
