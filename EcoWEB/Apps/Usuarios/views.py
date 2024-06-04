# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate

from django.contrib.auth import views as auth_views

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import ConsumidorSignUpForm, ProductorSignUpForm, LoginForm, ProfileEditForm, ProfileEditFormProd, ProductForm
from .models import Consumidor, Productor
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from google.oauth2 import service_account

from django.conf import settings

from django.urls import reverse_lazy

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialToken

import requests
from requests.exceptions import HTTPError
import json

import uuid
import threading
import hashlib
import binascii
import base64
import random
import string

import firebase_admin
from firebase_admin import credentials, auth, storage, initialize_app

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

    # Datos del consumidor a guardar
    consumidor_data = {
        "user": email
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
    database.child("Consumidores").child(uid).set(user_data)


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
    database.child("Productores").child(uid).set(user_data)

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


def generate_random_password(length=12):
    # Generar una contraseña aleatoria
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password


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
        'user': user,
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
            print(f"Datos del formulario: {form.cleaned_data}")  # Depuración
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
    return render(request, 'edit_profile_prod.html', {'form': form})

def home(request):
    return render(request, "index.html")

def log_out(request):
    logout(request)
    return redirect("login")

def clear_messages(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass


@login_required
def add_product(request):
    if request.method == 'POST':

        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            categoria = form.cleaned_data['categoria']
            descripcion = form.cleaned_data['descripcion']
            disponibilidad = form.cleaned_data['disponibilidad']
            precio = form.cleaned_data['precio']
            stock = form.cleaned_data['stock']
            imagen = request.FILES['imagen']

            # Generar un UUID para el producto
            producto_id = str(uuid.uuid4())

            # Subir imagen a Firebase Storage y obtener la URL
            bucket = storage.bucket()
            blob = bucket.blob(f'productos/{uuid.uuid4()}_{imagen.name}')
            blob.upload_from_file(imagen, content_type=imagen.content_type)
            blob.make_public()
            image_url = blob.public_url

            # Crear el objeto del producto
            producto = {
                "nombre": nombre,
                "categoria": categoria,
                "descripcion": descripcion,
                "disponibilidad": disponibilidad,
                "precio": float(precio),
                "stock": int(stock),
                "imagen": image_url
            }

            # Añadir el producto a la base de datos
            user_uid = obtener_uid(request)
            database.child("Productores").child(user_uid).child("productos").child(producto_id).set(producto)

            return redirect('products')
        else:
            print(form.errors)
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})


@login_required
def edit_product(request, product_id):
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        categoria = request.POST.get('categoria')
        stock = request.POST.get('stock')
        disponibilidad = 'disponibilidad' in request.POST

        # Subir imagen a Firebase Storage y obtener la URL
        if 'imagen' in request.FILES:
            imagen = request.FILES['imagen']            
            bucket = storage.bucket()
            blob = bucket.blob(f'productos/{uuid.uuid4()}_{imagen.name}')
            blob.upload_from_file(imagen, content_type=imagen.content_type)
            blob.make_public()
            image_url = blob.public_url

            # Actualizar los datos del producto en Firebase si se proporciona una imagen
            productos_ref = database.child("Productores").child(obtener_uid(request)).child("productos").child(product_id).update({
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": precio,
                "categoria": categoria,
                "disponibilidad": disponibilidad,
                "stock": stock,
                "imagen": image_url
            })
        else:
            # Actualizar los datos del producto en Firebase sin imagen
            productos_ref = database.child("Productores").child(obtener_uid(request)).child("productos").child(product_id).update({
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": precio,
                "categoria": categoria,
                "disponibilidad": disponibilidad,
                "stock": stock
            })

        return redirect('products')

    else:
        producto = database.child("Productores").child(obtener_uid(request)).child("productos").child(product_id)
        return render(request, 'edit_product.html', {'producto': producto})



@login_required
def delete_product(request, product_id):
    database.child("productos").child(product_id).remove()
    messages.success(request, 'Producto eliminado con éxito')
    return redirect('products')

@login_required
def products(request):
    uid = obtener_uid(request)
    productos_ref = database.child("Productores").child(uid).child("productos").get()

    productos = [
    {
        "id":product_id,
        "nombre": product_data.get("nombre", ""),
        "descripcion": product_data.get("descripcion", ""),
        "imagen": product_data.get("imagen", ""),
        "precio": product_data.get("precio", ""),
        "categoria": product_data.get("categoria", ""),
        "stock": product_data.get("stock", ""),
        "certificaciones_ecologicas": product_data.get("certificaciones_ecologicas", []),
        "disponibilidad": product_data.get("disponibilidad", False)
    } 
    for product_id, product_data in productos_ref.val().items()] if productos_ref and productos_ref.val() else print("No se encontraron productos para el usuario.")

    return render(request, 'products.html', {'productos': productos})




class CustomPasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'password_reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = 'localhost:8000'
        context['protocol'] = 'http'
        return context