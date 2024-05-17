# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import ConsumidorSignUpForm, ProductorSignUpForm, ProfileEditForm, LoginForm
from django.contrib.auth.decorators import login_required


import hashlib
import binascii
import base64

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

# Inicialización de la aplicación de Firebase
firebase = pyrebase.initialize_app(config)
database = firebase.database()
auth = firebase.auth()


# usu = auth.create_user_with_email_and_password("test@test.test", "Testpassword1!")
# if usu is not None:
#     print("Bien")

# awa = auth.sign_in_with_email_and_password("test@test.test", "Testpassword1!")
# if awa is not None:
#     print("Bienx2")


def signup_consumidor(request):
    clear_messages(request)
    if request.method == 'POST':
        form = ConsumidorSignUpForm(request.POST)

        try:
            user_firebase_info = auth.create_user_with_email_and_password(request.POST['email'], request.POST['password1'])
            # Obtener el UID del usuario desde la respuesta de Firebase Authentication y Guardar el usuario en la base de datos de Firebase
            uid = user_firebase_info['localId']
            guardar_consumidor_en_firebase(uid, request.POST['email'], request.POST['password1'])
            messages.success(request, 'Registro exitoso.')
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
                user_firebase_info = auth.create_user_with_email_and_password(user.email, user.password)
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

def guardar_consumidor_en_firebase(uid, email, password):

    # Datos del consumidor a guardar
    consumidor_data = {
        "user": email,
        "pass": password
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


def log_in(request):
    clear_messages(request)
    if request.method == 'POST':
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
                    messages.success(request, 'Login exitoso. Bienvenido a MARKETECO.')
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
            # messages.success(request, 'Inicio de sesión automático exitoso.')
            return redirect('index')
        else:
            messages.error(request, 'Error en el inicio de sesión automático.')

        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def verificar_credenciales_firebase(email, password):
    user_firebase_info = auth.sign_in_with_email_and_password(email, password)
    return user_firebase_info is not None

def perfil(request):
    return render(request, 'perfil.html')

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Actualizar los datos en Firebase
            user_data = {
                'email': user.email,
                'nombre': user.username,
                # Agrega otros campos según sea necesario
            }
            guardar_usuario_en_firebase(user.uid, user_data)
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