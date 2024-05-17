from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class ConsumidorSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Campo requerido. Por favor introduce una dirección mail válida.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # Utiliza el correo electrónico como nombre de usuario
        user.email = self.cleaned_data["email"]  # Establece el correo electrónico
        if commit:
            user.save()
        return user

class ProductorSignUpForm(UserCreationForm):

    email = forms.EmailField(max_length=254, help_text='Campo requerido. Por favor introduce una dirección mail válida.')
    username = forms.CharField(max_length=254, help_text='Por favor introduce un nombre de Usuario.')
    cif = forms.CharField(max_length=100, help_text='Campo requerido. Introduzca el CIF de la empresa.')
    telefono = forms.CharField(max_length=15, help_text='Campo requerido. Introduzca un número de teléfono.')

    class Meta:
        model = User
        fields = ('email', 'username', 'cif', 'telefono', 'password1', 'password2')

class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    direccion = forms.CharField(required=False, max_length=255)
    photo = forms.ImageField(required=False)

    class Meta (UserCreationForm.Meta):
        model = User
        fields = ('email', 'direccion', 'photo')

        def save(self, commit=True):
            user = super().save(commit=False)
            user.username = self.cleaned_data["email"]  # Utiliza el correo electrónico como nombre de usuario
            user.email = self.cleaned_data["email"]  # Establece el correo electrónico
            if commit:
                user.save()
            return user

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


    


   