# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import ConsumidorSignUpForm, ProductorSignUpForm

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

def signup_consumidor(request):
    if request.method == 'POST':
        form = ConsumidorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Guardar datos del consumidor en Firebase
            guardar_consumidor_en_firebase(user)
            return redirect('home')  # Redirigir a la página principal después del registro
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
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirigir a la página de perfil después del inicio de sesión exitoso
            return redirect('perfil')  
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def perfil(request):
    return render(request, 'perfil.html')
