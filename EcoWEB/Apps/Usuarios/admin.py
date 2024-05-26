from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Consumidor

class ConsumidorAdmin(UserAdmin):
    list_display = ('email', 'nombre', 'apellidos', 'is_staff', 'is_active')
    search_fields = ('email', 'nombre', 'apellidos')
    readonly_fields = ('fecha_alta',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Consumidor)
