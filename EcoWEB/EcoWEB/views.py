from django.shortcuts import render, redirect
import pyrebase
import firebase_admin
from firebase_admin import credentials, auth, storage, initialize_app

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

firebase = pyrebase.initialize_app(config=config)
authe = firebase.auth()
database = firebase.database()

def home(request):
    return render(request, 'index.html')

def mostrar_mejores_productos(request):
    productos_top = mejores_productos()

    context = {
        'productos_top': productos_top,
        'range': range(5, 0, -1)
    }

    return render(request, 'index.html', context)

def mejores_productos():

    productores_ref = database.child("Productores").get()
    productos = []

    # Recorrer cada productor y obtener sus productos
    for productor in productores_ref.each():
        productor_id = productor.key()
        productos_productor = productor.val().get('productos', {})
        for product_id, producto_data in productos_productor.items():
            producto_data['id'] = product_id
            productos.append(producto_data)

    # ordenar y devolver los 3 más valorados
    productos.sort(key=lambda x: x['valoracion'], reverse=True)
    return productos[:3]