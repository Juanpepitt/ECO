from django.db import models

from django.db import models
from Apps.Usuarios.models import Consumidor

class Conversacion(models.Model):
    participante1 = models.ForeignKey(Consumidor, related_name='conversaciones_participante1', on_delete=models.CASCADE)
    participante2 = models.ForeignKey(Consumidor, related_name='conversaciones_participante2', on_delete=models.CASCADE)
    ultimo_mensaje = models.TextField(blank=True, null=True)
    fecha_ultimo_mensaje = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Conversación entre {self.participante1.username} y {self.participante2.username}"

class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, related_name='mensajes', on_delete=models.CASCADE)
    emisor = models.ForeignKey(Consumidor, related_name='mensajes_enviados', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.emisor.username} en {self.conversacion}"