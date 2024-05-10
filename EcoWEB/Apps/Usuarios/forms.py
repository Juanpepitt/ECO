from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class ConsumidorSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

class ProductorSignUpForm(UserCreationForm):
    empresa = forms.CharField(max_length=100, help_text='Required. Inform the company name.')
    telefono = forms.CharField(max_length=15, help_text='Required. Inform the phone number.')

    class Meta:
        model = User
        fields = ('username', 'empresa', 'telefono', 'password1', 'password2')

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