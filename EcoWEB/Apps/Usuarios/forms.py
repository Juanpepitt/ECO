from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Consumidor, Productor

from django.core.exceptions import ValidationError
########################## Sign up
class ConsumidorSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, label='Correo electrónico', 
        help_text='Campo requerido. Por favor introduce una dirección mail válida.',
        widget=forms.EmailInput(attrs={'autofocus': True, 'style': 'width: 100%;'}))

    class Meta(UserCreationForm.Meta):
        model = Consumidor
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # Utiliza el correo electrónico como nombre de usuario
        user.email = self.cleaned_data["email"]  # Establece el correo electrónico
        if commit:
            user.save()
        return user


class ProductorSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, label='Correo electrónico', 
        help_text='Campo requerido. Por favor introduce una dirección mail válida.',
        widget=forms.EmailInput(attrs={'autofocus': True, 'style': 'width: 100%;'}))
    cif = forms.CharField(max_length=100, label= 'CIF/NIF', help_text='Campo requerido. Introduzca el CIF o NIF de la empresa.')

    class Meta:
        model = Productor
        fields = ('email', 'cif', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Consumidor.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con esta dirección de correo, si desea convertirse en productor o distribuidor, contacte con info@marketeco.shop')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_productor = True
        if(isinstance(user, Productor)):
            user.username = self.cleaned_data["email"]  # Utiliza el correo electrónico como nombre de usuario
            user.email = self.cleaned_data["email"]  # Establece el correo electrónico
            if commit:
                user.save()
            return user
##########################

########################## Login
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Correo electrónico',
        max_length=254,
        help_text='Campo requerido. Por favor, introduce una dirección mail válida.',
        widget=forms.EmailInput(attrs={'autofocus': True, 'style': 'width: 100%;'})
    )
    password = forms.CharField(
        label='Contraseña',
        max_length=254,
        help_text='Campo requerido. Por favor, introduce una contraseña válida.',
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True, 'style': 'width: 100%;'})
    )
    
    class Meta:
        fields = ['username', 'password']
##########################


########################## Profile Edit
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Consumidor
        fields = ['nombre', 'apellidos', 'email', 'direccion', 'telefono', 'photo']

class ProfileEditFormProd(forms.ModelForm):
    class Meta:
        model = Productor
        fields = ['nombre', 'apellidos', 'email', 'cif', 'direccion', 'telefono', 'photo']
##########################

##########################
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

CATEGORIAS_PRODUCTO = [
    ('Alimentación', 'Alimentación'),
    ('Tecnología', 'Tecnología'),
    ('Ropa', 'Ropa'),
    ('Hogar', 'Hogar'),
    ('Otros', 'Otros'),
]

class ProductForm(forms.Form):
    nombre = forms.CharField(label='Nombre de producto', max_length=150, strip=False, widget=forms.TextInput(attrs={'autofocus': True, 'style': 'width: 100%;'}), required=True)
    categoria = forms.ChoiceField(label='Categoría de producto', choices=CATEGORIAS_PRODUCTO, required=True, widget=forms.Select(attrs={'style': 'width: 100%;'}))
    descripcion = forms.CharField(label='Descripción del producto', widget=forms.Textarea(attrs={'autofocus': True, 'style': 'width: 100%;'}), strip=True)
    disponibilidad = forms.BooleanField(label='Disponible', required=False)
    precio = forms.DecimalField(label='Precio en €', max_digits=10, decimal_places=2, required=True)
    stock = forms.IntegerField(label='Número de unidades disponibles en Stock', required=False)
    imagen = forms.ImageField(label='Imagen del producto', required=False)
    # imagenes = forms.FileField(label='Imagen o imágenes del producto', widget=MultipleFileInput(attrs={'multiple': True, 'style': 'width: 100%;'}))
    # imagen_url = forms.URLField(required=False)
##########################