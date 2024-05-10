from django.contrib import admin
from .models import CustomUser, Consumidor, Productor

admin.site.register(CustomUser)
admin.site.register(Consumidor)
admin.site.register(Productor)
