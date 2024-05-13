from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class ConsumidorSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Campo requerido. Por favor introduce una dirección mail válida.')
    username = forms.CharField(max_length=254, help_text='Por favor introduce un nombre de Usuario.')

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

class ProductorSignUpForm(UserCreationForm):

    email = forms.EmailField(max_length=254, help_text='Campo requerido. Por favor introduce una dirección mail válida.')
    username = forms.CharField(max_length=254, help_text='Por favor introduce un nombre de Usuario.')
    cif = forms.CharField(max_length=100, help_text='Campo requerido. Introduzca el CIF de la empresa.')
    telefono = forms.CharField(max_length=15, help_text='Campo requerido. Introduzca un número de teléfono.')

    class Meta:
        model = User
        fields = ('email', 'username', 'cif', 'telefono', 'password1', 'password2')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico'
        }

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))