from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)



class Consumidor(AbstractUser):
    username = models.CharField('Username', blank=True, max_length=50)
    email = models.EmailField('Correo electrónico', unique=True, max_length=100)
    nombre = models.CharField('Nombre', max_length=254, blank=True, null=True)
    apellidos = models.CharField('Apellidos', max_length=254, blank=True, null=True)
    direccion = models.CharField('Direccion', max_length=255, blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True, null=True)
    fecha_alta = models.DateTimeField('Fecha de Alta', auto_now_add=True)
    photo = models.ImageField('Imagen de Perfil', upload_to='Usuarios/perfiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    # def __str__(self):
    #     return self.email

    # def has_perm(self, perm, obj=None):
    #     return self.is_superuser

    # def has_module_perms(self, app_label):
    #     return self.is_superuser


        
