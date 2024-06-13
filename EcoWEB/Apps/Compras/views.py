# Compras/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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

# #Firebase ADMIN
# cred = credentials.Certificate("Apps/Usuarios/ecoweb-fc73c-firebase-adminsdk-20hmv-feea5a9108.json")
# firebase_admin.initialize_app(cred, {'storageBucket': 'ecoweb-fc73c.appspot.com'})
# bucket = storage.bucket()

# Inicialización de la aplicación de Firebase
firebase = pyrebase.initialize_app(config)
database = firebase.database()
auth_firebase = firebase.auth()

@login_required
def carrito (request):

    uid = obtener_uid(request)
    consumer_data = database.child("Consumidores").child(uid)
    carrito = consumer_data.get('carrito', {}).val() if consumer_data else {}

    context = {
        'carrito': carrito
    }

    return render(request, "carrito.html", context)


@login_required
def add_carrito(request, producto_id):

    return redirect('detalle_producto', producto_id=producto_id)

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