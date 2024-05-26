from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Consumidor

# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('email', 'first_name', 'last_name', 'is_staff', 'fecha_alta')
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'direccion', 'telefono', 'photo')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined', 'fecha_alta')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2'),
#         }),
#     )
#     search_fields = ('email', 'first_name', 'last_name')
#     ordering = ('email',)

admin.site.register(Consumidor)
