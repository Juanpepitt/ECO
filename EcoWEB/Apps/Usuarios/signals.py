from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Consumidor

@receiver(user_signed_up)
def create_consumidor_on_signup(sender, request, user, **kwargs):
    # Extraer los datos adicionales de la respuesta de autenticación
    sociallogin = kwargs.get('sociallogin', None)
    if sociallogin:
        extra_data = sociallogin.account.extra_data
        first_name = extra_data.get('given_name', '')
        last_name = extra_data.get('family_name', '')
        picture_url = extra_data.get('picture', '')
        # Para la dirección, normalmente Google no proporciona esta información directamente
        # pero se puede obtener mediante una API de perfil de usuario si estuviera disponible

        # Crear o actualizar el perfil del Consumidor
        consumidor, created = Consumidor.objects.get_or_create(
            email=user.email,
            defaults={
                'nombre': first_name,
                'apellidos': last_name,
                'username': user.username,
                'photo_url': picture_url,
                # Añade otros campos por defecto aquí si es necesario
            }
        )

        # Si el Consumidor ya existe, actualizar los nombres y la foto si están vacíos
        if not created:
            if not consumidor.nombre:
                consumidor.nombre = first_name
            if not consumidor.apellidos:
                consumidor.apellidos = last_name
            if not consumidor.photo_url:
                consumidor.photo_url = picture_url
            consumidor.save()
    else:
        # Si no hay datos sociales disponibles, crear el Consumidor solo con el email
        Consumidor.objects.get_or_create(
            email=user.email,
            defaults={'username': user.username}
        )