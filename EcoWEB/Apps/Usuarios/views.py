# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import ConsumidorSignUpForm, ProductorSignUpForm, ProfileEditForm, EmailAuthenticationForm
from django.contrib.auth.decorators import login_required

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

def signup_consumidor(request):
    if request.method == 'POST':
        form = ConsumidorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                # Crear el usuario en Firebase Authentication
                user_firebase_info = auth.create_user_with_email_and_password(user.username, user.password)
                # Obtener el UID del usuario desde la respuesta de Firebase Authentication y Guardar el usuario en la base de datos de Firebase
                uid = user_firebase_info['localId']
                guardar_consumidor_en_firebase(uid, user.email, user.username, user.password)
                print("Consumidor registrado con éxito en Django y Firebase")
                return redirect('login')
            except Exception as e:
                error_code = e.args[0]['error']['message']
                if error_code == 'EMAIL_EXISTS':
                    messages.error(request, 'El usuario ya existe. Por favor, inicia sesión.')
                else:
                    messages.error(request, 'Error al crear el usuario en Firebase.')
                user.delete() #revertir usuario de django
                print("Error al crear el usuario en Firebase:", e)
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

def guardar_consumidor_en_firebase(uid, email, nombre, password):

    # Datos del consumidor a guardar
    consumidor_data = {
        "nombre": nombre,
        "email": email,
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
    if request.method == 'POST':
        print(request.POST)
        form = EmailAuthenticationForm(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Verificar credenciales en Firebase
            if verificar_credenciales_firebase(email, password):
                # Si las credenciales son válidas, iniciar sesión en Django
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    # Redirigir a la página de perfil después del inicio de sesión exitoso
                    return redirect('perfil')
                else:
                    # Manejar el caso en que el usuario no exista en Django
                    # o las credenciales no coincidan
                    print("no existe en Django")
            else:
                # Manejar el caso en que las credenciales no sean válidas en Firebase
                print ("no es válido en Firebase")
        else:
            print("no es válido el formulario: ")
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def verificar_credenciales_firebase(email, password):

    try:
        auth.sign_in_with_email_and_password(email, password)
        return True
    except:
        return False


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
    return render(request, "index")

def log_out(request):
    logout(request)
    return redirect("signup_consumidor")