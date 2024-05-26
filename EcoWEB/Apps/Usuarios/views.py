# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate

from django.contrib.auth import views as auth_views

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import ConsumidorSignUpForm, ProductorSignUpForm, ProfileEditForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from google.oauth2 import service_account

from django.conf import settings

from django.urls import reverse_lazy

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialToken

import threading

import hashlib
import binascii
import base64
import random
import string

import firebase_admin
from firebase_admin import credentials, auth

import pyrebase

# Configuración de Firebase
config={
    "apiKey": "AIzaSyDuSSwDlasTMzZFoYgbKUHvAWOsG8a9lOo",
    "authDomain": "ecoweb-fc73c.firebaseapp.com",
    "databaseURL": "https://ecoweb-fc73c-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "ecoweb-fc73c",
    "storageBucket": "ecoweb-fc73c.appspot.com",
    "messagingSenderId": "725619478235",
    "appId": "1:725619478235:web:7c49e52eead0b7e96546fe",
    "measurementId": "G-YXW94VQWHH"
}

#Firebase ADMIN
cred = credentials.Certificate("Apps/Usuarios/ecoweb-fc73c-firebase-adminsdk-20hmv-feea5a9108.json")
firebase_admin.initialize_app(cred)

# Inicialización de la aplicación de Firebase
firebase = pyrebase.initialize_app(config)
database = firebase.database()
auth_firebase = firebase.auth()


def signup_consumidor(request):
    clear_messages(request)
    if request.method == 'POST' and request.POST['password1'] == request.POST['password2']:
        try:
            form = ConsumidorSignUpForm(request.POST)
            user_firebase_info = auth_firebase.create_user_with_email_and_password(request.POST['email'], request.POST['password1'])
            # Obtener el UID del usuario desde la respuesta de Firebase Authentication y Guardar el usuario en la base de datos de Firebase
            uid = user_firebase_info['localId']
            guardar_consumidor_en_firebase(uid, request.POST['email'])
            print("Consumidor registrado con éxito en Django y Firebase")
            # Guardar las credenciales en la sesión
            request.session['username'] = request.POST['email']
            request.session['password'] = request.POST['password1']

        except Exception as e:
            error_code = e.args[0]['error']['message']
            if error_code == 'EMAIL_EXISTS':
                messages.error(request, 'El usuario ya existe. Por favor, inicia sesión.')
            else:
                messages.error(request, 'Error al crear el usuario en Firebase.')
            user.delete() #revertir usuario de django
            print("Error al crear el usuario en Firebase:", e)

        #creación en Django
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡¡Registro con éxito!!')
            messages.success(request, 'Se ha iniciado sesión.')
            return redirect('login')    
    else:
        form = ConsumidorSignUpForm()
    return render(request, 'signup_consumidor.html', {'form': form})


def signup_productor(request):
    if request.method == 'POST':
        form = ProductorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                # Crear el usuario en Firebase Authentication
                user_firebase_info = auth_firebase.create_user_with_email_and_password(user.email, user.password)
                # Obtener el UID del usuario desde la respuesta de Firebase Authentication y Guardar el usuario en la base de datos de Firebase
                uid = user_firebase_info['localId']
                guardar_productor_en_firebase(uid, user.email, user.username, user.password)
                return redirect('home')
            except Exception as e:
                error_code = e.args[0]['error']['message']
                if error_code == 'EMAIL_EXISTS':
                    messages.error(request, 'El usuario ya existe. Por favor, inicia sesión.')
                else:
                    messages.error(request, 'Error al crear el usuario en Firebase.')
                user.delete() #revertir usuario de django
                print("Error al crear el usuario en Firebase:", e)
    else:
        form = ProductorSignUpForm()
    return render(request, 'signup_productor.html', {'form': form})

def guardar_consumidor_en_firebase(uid, email):

    # Datos del consumidor a guardar
    consumidor_data = {
        "user": email
    }

    # Guardar el consumidor en la base de datos
    database.child("Consumidores").child(uid).set(consumidor_data)

def guardar_productor_en_firebase(uid, email, nombre, password):

    # Datos del consumidor a guardar
    productor_data = {
        "nombre": nombre,
        "email": email,
        "pass": password
    }

    # Guardar el consumidor en la base de datos
    database.child("Productores").child(uid).set(productor_data)


def log_in_2(request):
    if request.method == 'POST':
        clear_messages(request)
        form = LoginForm(request, request.POST)
        email_firebase = request.POST['username']
        pass_firebase = request.POST['password']

        if form.is_valid():            
            # Verificar credenciales en Firebase
            if verificar_credenciales_firebase(email_firebase, pass_firebase):
                # Si las credenciales son válidas, iniciar sesión en Django
                
                email = form.cleaned_data['username']
                password = form.cleaned_data['password']
                
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)
                    
                    # Redirigir a la página de perfil después del inicio de sesión exitoso
                    messages.success(request, '¡¡Bienvenido a MARKETECO de nuevo!!')
                    return redirect('index')
                else:
                    messages.error(request, 'Nombre de usuario o contraseña incorrectos.')   
                    print("no existe en Django")
            else:
                messages.error(request, 'No se ha registrado bien')
                print ("no es válido en Firebase")
        else:
            print("no es válido el formulario: ")
    else:
        # Intentar el login automático primero en Firebase y luego en Django
        username = request.session.pop('username', None)
        password = request.session.pop('password', None)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            verificar_credenciales_firebase(username, password)
            login(request, user)
            return redirect('index')

        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def log_in(request):
    if request.method == 'POST':
        clear_messages(request)
        form = LoginForm(data=request.POST) 
        if form.is_valid():            
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '¡Bienvenido a MARKETECO de nuevo!')
                return redirect('index')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, '¡Algo salió mal! Por favor, verifica tus datos.')  # Agregar un mensaje de error general si el formulario no es válido
    else:
        # Intentar el login automático primero en Firebase y luego en Django
        username = request.session.pop('username', None)
        password = request.session.pop('password', None)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')

        form = LoginForm()  # Crear una instancia de LoginForm sin pasar datos adicionales

    return render(request, 'login.html', {'form': form})


def verificar_credenciales_firebase(email, password):
    user_firebase_info = auth_firebase.sign_in_with_email_and_password(email, password)
    return user_firebase_info is not None


def generate_random_password(length=12):
    # Generar una contraseña aleatoria
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password


def enviar_mail_2(request, email, password):
    send_mail(
        'Registro Exitoso en MARKETECO',
        f'Hola, {request.user.username}!\n\nTu registro ha sido exitoso. Aquí están tus credenciales:\n\nEmail: {email}\nContraseña: {password}\n\nPor favor, guarda esta información en un lugar seguro.',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

def enviar_mail(request):
    print(request)
    send_mail(
        'Registro Exitoso en MARKETECO',
        f'Hola, {request.user.username}!\n\nTu registro ha sido exitoso.',
        settings.EMAIL_HOST_USER,
        [request.user.username],
        fail_silently=False,
    )
    print(f'email enviado a {request.user.username}')
    return redirect('password_reset_done')

@login_required
def firebase_register(request):

    try:
        social_account_user = SocialAccount.objects.get(user=request.user, provider='google')

        if social_account_user:
            email = social_account_user.extra_data.get('email')
            if email:
                password = generate_random_password()
                try:
                    user_firebase_info = auth_firebase.create_user_with_email_and_password(email, password)
                    # Obtener el UID del usuario desde la respuesta de Firebase Authentication y Guardar el usuario en la base de datos de Firebase
                    uid = user_firebase_info['localId']
                    guardar_consumidor_en_firebase(uid, email)
                    messages.success(request, 'Registrado con éxito en Marketeco')
                    print("Consumidor registrado con éxito en Django y Firebase")
                    
                    # Enviar correo electrónico con la contraseña
                    # thread = threading.Thread(target=enviar_mail, 
                    #     args=(request, email, password, ))
                    # thread.start()

                except Exception as e:
                    print('Error al registrar el usuario en Firebase.')
                    print(e)

                    

                
            else:
                print('No se pudo obtener el correo electrónico del usuario.')

        else:
            print('No se pudo obtener la cuenta de Google.')

    except Exception as e:
        messages.error(request, 'Error al registrar.')
        print(e)
    
    return redirect('index')

def obtener_uid(request):
    try:
        user = auth.get_user_by_email(str(request.user))
        uid = user.uid
        print(f'UID del usuario: {uid}')
    except firebase_admin.auth.UserNotFoundError:
        print(f'No se encontró un usuario con el correo electrónico {email}')
    except Exception as e:
        print(f'Error al obtener el usuario: {str(e)}')
    return uid


@login_required
def perfil(request):
    user = request.user
    
    # Pasar los datos del usuario al contexto de la plantilla
    context = {
        'user': user,
    }

    # Renderizar la plantilla y pasar el contexto
    return render(request, 'perfil.html', context)

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            print(f"Datos del formulario: {form.cleaned_data}")  # Depuración
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            # Actualizar los datos en Firebase
            # user_data = {
            #     'email': request.POST['email'],
            #     'password': request.POST['password'],
            # }
            #actualizar los datos en firebase authentication y bbdd
            guardar_consumidor_en_firebase(user.uid, user_data)
            return redirect('perfil')  # Redirige al perfil después de la edición
    else:
        form = ProfileEditForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})


def home(request):
    return render(request, "index.html")

def log_out(request):
    logout(request)
    return redirect("login")

def clear_messages(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass


class CustomPasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'password_reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = 'localhost:8000'
        context['protocol'] = 'http'
        return context