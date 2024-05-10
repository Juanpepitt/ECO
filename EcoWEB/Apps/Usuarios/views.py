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
            # Crear el usuario en Firebase Authentication
            try:
                auth.create_user_with_email_and_password(user.email, user.password)
                return redirect('home')  # Redirigir a la página principal después del registro
            except Exception as e:
                # Manejar errores al crear el usuario en Firebase
                print("Error al crear el usuario en Firebase:", e)
                # También puedes revertir el registro del usuario en Django si falla en Firebase
                user.delete()
    else:
        form = ConsumidorSignUpForm()
    return render(request, 'signup_consumidor.html', {'form': form})

def signup_productor(request):
    if request.method == 'POST':
        form = ProductorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Guardar datos del productor en Firebase
            guardar_productor_en_firebase(user)
            return redirect('home')  # Redirigir a la página principal después del registro
    else:
        form = ProductorSignUpForm()
    return render(request, 'signup_productor.html', {'form': form})


def guardar_consumidor_en_firebase(user):
    database = firebase.database()

    # Datos del consumidor a guardar
    consumidor_data = {
        "nombre": user.username,
        "email": user.email,
        # Otros datos del consumidor
    }

    # Guardar el consumidor en la base de datos
    database.child("Consumidores").push(consumidor_data)

def guardar_productor_en_firebase(user):
    database = firebase.database()

    # Datos del productor a guardar
    productor_data = {
        "nombre": user.username,
        "email": user.email,
        # Otros datos del productor
    }

    # Guardar el productor en la base de datos
    database.child("Productores").push(productor_data)

def log_in(request):
    if request.method == 'POST':
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
            print("no es válido el formulario")
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def verificar_credenciales_firebase(email, password):
    # Lógica para verificar las credenciales en Firebase
    return True  # Devuelve True si las credenciales son válidas en Firebase



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

def guardar_usuario_en_firebase(uid, user_data):
    database = firebase.database()
    database.child('Consumidores').child(uid).update(user_data)

