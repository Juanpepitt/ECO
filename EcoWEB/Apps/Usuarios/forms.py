from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Consumidor, Productor

class ConsumidorSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, label='Correo electrónico', help_text='Campo requerido. Por favor introduce una dirección mail válida.')
    # nombre = forms.CharField(max_length=254, help_text='Campo requerido. Por favor introduce tu nombre.')

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
    email = forms.EmailField(max_length=254, label='Correo electrónico', help_text='Campo requerido. Por favor introduce una dirección mail válida.')
    cif = forms.CharField(max_length=100, label= 'CIF/NIF', help_text='Campo requerido. Introduzca el CIF de la empresa.')

    class Meta:
        model = Productor
        fields = ('email', 'cif', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # Utiliza el correo electrónico como nombre de usuario
        user.email = self.cleaned_data["email"]  # Establece el correo electrónico
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Consumidor
        fields = ['nombre', 'apellidos', 'email', 'direccion', 'telefono', 'photo']

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
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


    


   