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

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField('auth.Group', related_name='users', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='users', blank=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

# class Consumidor(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='consumidor')

#     def __str__(self):
#         return self.user.email

# class Productor(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='productor')

#     def __str__(self):
#         return self.user.email
