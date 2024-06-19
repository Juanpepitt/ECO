# Usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate

from django.contrib.auth import views as auth_views

from django.contrib import messages
from .forms import ConsumidorSignUpForm, ProductorSignUpForm, LoginForm, ProfileEditForm, ProfileEditFormProd
from .models import Consumidor, Productor
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from google.oauth2 import service_account
from django.core.exceptions import ValidationError

from django.conf import settings

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialToken

import requests
from requests.exceptions import HTTPError
import json
import string

import firebase_admin
from firebase_admin import auth, storage

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
cred = firebase_admin.credentials.Certificate("Apps/Usuarios/ecoweb-fc73c-firebase-adminsdk-20hmv-feea5a9108.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'ecoweb-fc73c.appspot.com'})
bucket = storage.bucket()

# Inicialización de la aplicación de Firebase
firebase = pyrebase.initialize_app(config)
database = firebase.database()
auth_firebase = firebase.auth()


def signup_consumidor(request):
    clear_messages(request)
    if request.method == 'POST' and request.POST['password1'] == request.POST['password2'] and not verificar_usuario_en_firebase_auth(request.POST['email']):
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

        except requests.HTTPError as e:
                    error_json = e.args[1]
                    error = json.loads(error_json)['error']['message']
                    if error == "EMAIL_EXISTS":
                        print('El usuario ya se encuentra en Firebase. Por favor, revisar Firebase.')

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
    clear_messages(request)
    if request.method == 'POST' and request.POST['password1'] == request.POST['password2'] and not verificar_usuario_en_firebase_auth(request.POST['email']):
        try:
            form = ProductorSignUpForm(request.POST)
            user_firebase_info = auth_firebase.create_user_with_email_and_password(request.POST['email'], request.POST['password1'])
            # Obtener el UID del usuario desde la respuesta de Firebase Authentication y Guardar el usuario en la base de datos de Firebase
            uid = user_firebase_info['localId']
            guardar_productor_en_firebase(uid, request.POST['email'], request.POST['cif'])
            print("Productor registrado con éxito en Django y Firebase")
            # Guardar las credenciales en la sesión
            request.session['username'] = request.POST['email']
            request.session['password'] = request.POST['password1']

        except requests.HTTPError as e:
                    error_json = e.args[1]
                    error = json.loads(error_json)['error']['message']
                    if error == "EMAIL_EXISTS":
                        print('El usuario ya se encuentra en Firebase. Por favor, revisar Firebase.')

        except Exception as e:
            error_code = e.args[0]['error']['message']
            if error_code == 'EMAIL_EXISTS':
                messages.error(request, 'El usuario ya existe. Por favor, inicia sesión.')

            user.delete() #revertir usuario de django
            print("Error al crear el usuario en Firebase:", e)

        #creación en Django
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡¡Registro con éxito!!')
            messages.success(request, 'Se ha iniciado sesión.')
            return redirect('login')
        else:
            print("No se ha creado")    
    else:
        form = ProductorSignUpForm()
    return render(request, 'signup_productor.html', {'form': form})

def guardar_consumidor_en_firebase(uid, email):
    carrito = {}

    # Datos del consumidor a guardar
    consumidor_data = {
        "user": email,
        "carrito": carrito
    }

    # Guardar el consumidor en la base de datos
    database.child("Consumidores").child(uid).set(consumidor_data)

def verificar_usuario_en_firebase_auth(email):
    api_key = config["apiKey"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
    payload = json.dumps({"email": [email]})
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        users = response.json().get("users", [])
        if users:
            return True
    return False

def actualizar_consumidor_en_firebase(request, user_data):
    #Obtener el uid del usuario actual
    uid = obtener_uid(request=request)
    database.child("Consumidores").child(uid).update(user_data)

def guardar_productor_en_firebase(uid, email, cif):

    # Datos del consumidor a guardar
    productor_data = {
        "user": email,
        "cif": cif,
        "productos": {}
    }

    # Guardar el consumidor en la base de datos
    database.child("Productores").child(uid).set(productor_data)

def actualizar_productor_en_firebase(request, user_data):
    #Obtener el uid del usuario actual
    uid = obtener_uid(request=request)
    database.child("Productores").child(uid).update(user_data)

def log_in(request):
    if request.method == 'POST':
        clear_messages(request)
        form = LoginForm(data=request.POST)
        if form.is_valid():            
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request=request, username=email, password=password)
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
                    # Obtener el UID del usuario desde la respuesta de Firebase Authentication y Guardar el usuario en la base de datos de Firebase
                    # Primero se comprueba de qué tipo es el usuario y se registra
                    user_firebase_info = auth_firebase.create_user_with_email_and_password(email, password)
                    uid = user_firebase_info['localId']
                    
                    user = request.user
                    if hasattr(user, 'productor'):
                        user = user.productor

                    if(isinstance(user, Productor)):
                        guardar_productor_en_firebase(uid, email)
                    else:
                        guardar_consumidor_en_firebase(uid, email)
                    
                    messages.success(request, 'Registrado con éxito en Marketeco')
                    print("Consumidor registrado con éxito en Django y Firebase")
                except requests.HTTPError as e:
                    error_json = e.args[1]
                    error = json.loads(error_json)['error']['message']
                    if error == "EMAIL_EXISTS":
                        print('El usuario ya se encuentra en Firebase. Por favor, revisar Firebase.')
                except Exception as e:
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
        # print(f'UID del usuario: {uid}')
    except firebase_admin.auth.UserNotFoundError:
        print(f'No se encontró un usuario con el correo electrónico {email}')
    except Exception as e:
        print(f'Error al obtener el usuario: {str(e)}')
    return uid

@login_required
def perfil(request):
    user = request.user

    if hasattr(user, 'productor'):
        user = user.productor
    
    context = {
        'user': user
    }

    if(isinstance(user, Productor)):
        return render(request, 'perfil_prod.html', context)
    else:
        return render(request, 'perfil.html', context)

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            # Actualizar los datos en Firebase
            user_data = {
                'user': request.POST['email'],
                'nombre': request.POST['nombre'],
                'apellidos': request.POST['apellidos'],
                'direccion': request.POST['direccion'],
                'telefono': request.POST['telefono']
            }

            actualizar_consumidor_en_firebase(request, user_data)
            return redirect('perfil')  # Redirige al perfil después de la edición
    else:
        form = ProfileEditForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def edit_profile_prod(request):
    user = request.user

    uid = obtener_uid(request=request)
    productor_data = database.child("Productores").child(uid).get().val()

    if request.method == 'POST':
        form = ProfileEditFormProd(request.POST, request.FILES, instance=user)
        if form.is_valid():
            print(f"Datos del formulario: {form.cleaned_data}")  # Depuración
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            # Actualizar los datos en Firebase
            user_data = {
                'user': request.POST['email'],
                'nombre': request.POST['nombre'],
                'cif': request.POST['cif'],
                'apellidos': request.POST['apellidos'],
                'direccion': request.POST['direccion'],
                'telefono': request.POST['telefono']
            }

            actualizar_productor_en_firebase(request, user_data)
            return redirect('perfil')  # Redirige al perfil después de la edición
    else:
        form = ProfileEditFormProd(instance=user)

    context = {
        'form': form,
        'productor_data': productor_data
    }
    
    return render(request, 'edit_profile_prod.html', context)

@login_required
def muestra_productores(request):
    user = request.user
    productores = Productor.objects.all()

    productores_data = []
    for productor in productores:
        productores_data.append({
            'id': productor.id,
            'email': productor.email,
            'nombre': productor.nombre,
            'apellidos': productor.apellidos,
            'telefono': productor.telefono,
            'imagen': productor.photo
        })

    context = {
        'productores': productores_data,
        'user': user
    }

    return render(request, 'muestra_productores.html', context)

@login_required
def eliminar_usuario(request):

    user = request.user
    uid = obtener_uid(request)

    if hasattr(user, 'productor'):
        user = user.productor
    
    context = {
        'user': user
    }

    if(isinstance(user, Productor)):
        database.child("Productores").child(uid).remove()
    else:
        database.child("Consumidores").child(uid).remove()

    auth.delete_user(uid)
    user.delete()

    logout(request)

    return redirect("/")

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