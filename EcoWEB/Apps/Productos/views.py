# Productos/views.py
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings

from .forms import ProductForm

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

# #Firebase ADMIN
# cred = credentials.Certificate("Apps/Usuarios/ecoweb-fc73c-firebase-adminsdk-20hmv-feea5a9108.json")
# firebase_admin.initialize_app(cred, {'storageBucket': 'ecoweb-fc73c.appspot.com'})
# bucket = storage.bucket()

# Inicialización de la aplicación de Firebase
firebase = pyrebase.initialize_app(config)
database = firebase.database()
auth_firebase = firebase.auth()


def home(request):
    return render(request, "index.html")

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
            imagen = request.FILES.get('imagen')

            # Generar un UUID para el producto
            producto_id = str(uuid.uuid4())

            image_url = None
            if imagen:
                # Subir imagen a Firebase Storage y obtener la URL
                bucket = storage.bucket()
                blob = bucket.blob(f'productos/{uuid.uuid4()}_{imagen.name}')
                blob.upload_from_file(imagen, content_type=imagen.content_type)
                blob.make_public()
                image_url = blob.public_url
            else:
                image_url = "https://dummyimage.com/600x400/3d003d/ffffff.png&text=Imagen+de+producto"

            # Crear el objeto del producto
            producto = {
                "nombre": nombre,
                "categoria": categoria,
                "descripcion": descripcion,
                "disponibilidad": disponibilidad,
                "precio": float(precio),
                "stock": int(stock) if stock else None,
                "imagen": image_url,
                "valoracion": int(0),
                "valoraciones": int(0)
                
            }

            # Añadir el producto a la base de datos
            user_uid = obtener_uid(request)
            database.child("Productores").child(user_uid).child("productos").child(producto_id).set(producto)
            messages.success(request, nombre+' añadido con éxito')
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

        # Convertir precio de coma a punto
        try:
            precio = precio.replace(',', '.')
            precio = float(precio)
            if precio <= 0:
                raise ValidationError('El precio debe ser mayor que 0.')
        except (ValueError, ValidationError) as e:
            messages.error(request, str(e))
            return render(request, 'edit_product.html', {
                'producto': {
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'precio': precio,
                    'categoria': categoria,
                    'stock': stock,
                    'disponibilidad': disponibilidad,
                }
            })

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
        messages.success(request, nombre+' editado con éxito')

        return redirect('products')

    else:
        producto = database.child("Productores").child(obtener_uid(request)).child("productos").child(product_id)
        return render(request, 'edit_product.html', {'producto': producto})
        
@login_required
def delete_product(request, product_id):
    uid = obtener_uid(request)
    productos_ref = database.child("Productores").child(uid).child("productos").child(product_id).remove()
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
        "disponibilidad": product_data.get("disponibilidad", False)
    } 
    
    for product_id, product_data in productos_ref.val().items()] if productos_ref and productos_ref.val() else print("No se encontraron productos para el usuario.")

    opciones_categoria = ['Alimentación', 'Tecnología', 'Ropa', 'Hogar', 'Otros']

    # Filtrar por categoría si se especifica
    filtro_categoria = request.GET.get('categoria')
    if filtro_categoria:
        productos = [producto for producto in productos if producto.get('categoria') == filtro_categoria]

    # Dejar categoría seleccionada al usar desplegable
    selected_categoria = filtro_categoria if filtro_categoria in opciones_categoria else None

    context = {
        'productos': productos,
        'opciones_categoria': opciones_categoria,
        'selected_categoria': selected_categoria,
    }

    return render(request, 'products.html', context)

def lista_productos(request):
    productos_ref = database.child("Productores").get()
    productos = []
    categorias = set()
    productores = set()

    try:
        if (productos_ref):
            # Recorrer cada productor y obtener sus productos
            for productor in productos_ref.each():
                productor_id = productor.key()
                productor_nombre = productor.val().get('user', 'Desconocido')
                productos_productor = productor.val().get('productos', {})
                for product_id, producto_data in productos_productor.items():
                    producto_data['id'] = product_id
                    producto_data['productor'] = productor_nombre
                    if 'precio' in producto_data:
                        try:
                            producto_data['precio'] = float(producto_data['precio'])
                        except (ValueError, TypeError):
                            producto_data['precio'] = 0
                    
                    if 'valoracion' in producto_data:
                        try:
                            producto_data['valoracion'] = int(producto_data['valoracion'])
                        except (ValueError, TypeError):
                            producto_data['valoracion'] = 0

                    productos.append(producto_data)
                    categorias.add(producto_data.get('categoria', 'Otros'))
                    productores.add(productor_nombre)
    except (ValueError, TypeError) as e:
        print(e)

    # Filtrar por nombre de producto si se especifica
    buscar = request.GET.get('buscar')
    if buscar:
        productos = [producto for producto in productos if buscar.lower() in producto.get('nombre', '').lower()]

    # Filtrar por categoría si se especifica
    filtro_categoria = request.GET.get('categoria')
    if filtro_categoria:
        productos = [producto for producto in productos if producto.get('categoria') == filtro_categoria]

    # Filtrar por productor si se especifica
    filtro_productor = request.GET.get('productor')
    if filtro_productor:
        productos = [producto for producto in productos if producto.get('productor') == filtro_productor]

    #dejar categoría seleccionada al usar desplegable
    selected_categoria = filtro_categoria if filtro_categoria in categorias else None
    #dejar productor seleccionado al usar desplegable
    selected_productor = filtro_productor if filtro_productor in productores else None

    # Ordenar productos
    ordenar_por = request.GET.get('ordenar_por')
    if ordenar_por == 'precio_ascendente':
        productos = sorted(productos, key=lambda x: x.get('precio', 0))
    elif ordenar_por == 'precio_descendente':
        productos = sorted(productos, key=lambda x: x.get('precio', 0), reverse=True)
    elif ordenar_por == 'valoracion':
        productos = sorted(productos, key=lambda x: x.get('valoracion', 0), reverse=True)

    #dejar ordenar seleccionado al usar desplegable
    ordenar_por = request.GET.get('ordenar_por')
    selected_ordenar_por = ordenar_por if ordenar_por in ['precio_ascendente', 'precio_descendente', 'valoracion'] else None

    context = {
        'list_products': productos, 
        'categorias': categorias, 
        'productores': productores,
        'range': range(5, 0, -1),
        'selected_categoria': selected_categoria, 
        'selected_productor': selected_productor, 
        'selected_ordenar_por': selected_ordenar_por,
        'buscar':buscar
        }
    return render(request, 'list_products.html', context)

def detalle_producto(request, producto_id):
    productores_ref = database.child("Productores").get()
    producto = None

    for productor in productores_ref.each():
        productos_productor = productor.val().get('productos', {})
        if producto_id in productos_productor:
            producto = productos_productor[producto_id]
            producto['id'] = producto_id
            context = {
                'producto': producto,
                'range': range(5, 0, -1)
            }
            break

    if producto is None:
        return render(request, '404.html')

    return render(request, 'detalle_producto.html', context)


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

