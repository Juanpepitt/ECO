# Compras/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Apps.Usuarios.models import Consumidor, Productor
from django.conf import settings
import firebase_admin
from firebase_admin import credentials, auth, storage, initialize_app

import stripe
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

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def ver_carrito (request):

    user = request.user
    uid = obtener_uid(request)
    
    if hasattr(user, 'productor'):
        user = user.productor

    if(isinstance(user, Productor)):
        user_ref = database.child("Productores").child(uid)
    else:
        user_ref = database.child("Consumidores").child(uid)

    user_data = user_ref.get().val()
    carrito_actual = user_data.get('carrito', {})

    total = 0

    # Itera sobre los productos en el carrito y calcula el total
    for productoid, producto in carrito_actual.items():
        cantidad = producto.get('cantidad', 0)
        precio = producto.get('precio', 0)
        total += cantidad * precio

    context = {
        'carrito': carrito_actual,
        'total': total
    }

    return render(request, "carrito.html", context)

@login_required
def add_carrito(request, producto_id):

    user = request.user
    uid = obtener_uid(request)

    if hasattr(user, 'productor'):
        user = user.productor

    if(isinstance(user, Productor)):
        user_ref = database.child("Productores").child(uid)
    else:
        user_ref = database.child("Consumidores").child(uid)
    
    user_data = user_ref.get().val()

    if not user_data:
        messages.error(request, 'Usuario no encontrado')
        return redirect('/productos/lista_productos/')

    carrito_actual = user_data.get('carrito', {})

    productos_ref = database.child("Productores").get()
    producto_data = None

    # Recorrer cada productor y obtener el producto
    for productor in productos_ref.each():
        productos_productor = productor.val().get('productos', {})
        if producto_id in productos_productor:
            producto_data = productos_productor[producto_id]
            break

    if producto_data:
        if producto_id in carrito_actual and 'cantidad' in carrito_actual[producto_id]:
            carrito_actual[producto_id]['cantidad'] += 1
        else:
            carrito_actual[producto_id] = {
                'nombre': producto_data['nombre'],
                'categoria': producto_data['categoria'],
                'descripcion': producto_data['descripcion'],
                'imagen': producto_data['imagen'],
                'precio': producto_data['precio'],
                'cantidad': 1  # Inicializamos la cantidad en 1
            }

        # Actualizar el carrito en la base de datos
        if(isinstance(user, Productor)):
            database.child("Productores").child(uid).child('carrito').set(carrito_actual)
        else:
            database.child("Consumidores").child(uid).child('carrito').set(carrito_actual)

        messages.success(request, f'{producto_data["nombre"]} añadido con éxito a la cesta')
    else:
        messages.error(request, 'Producto no encontrado')

    return redirect('list_products')

@login_required
def eliminar_producto_carrito(request, producto_id):

    user = request.user
    uid = obtener_uid(request)

    if hasattr(user, 'productor'):
        user = user.productor

    if(isinstance(user, Productor)):
        user_ref = database.child("Productores").child(uid)
    else:
        user_ref = database.child("Consumidores").child(uid)

    user_data = user_ref.get().val()

    if user_data and 'carrito' in user_data and producto_id in user_data['carrito']:
        try:
            if(isinstance(user, Productor)):
                database.child("Productores").child(uid).child('carrito').child(producto_id).remove()
            else:
                database.child("Consumidores").child(uid).child('carrito').child(producto_id).remove()
            messages.success(request, 'Producto eliminado de la cesta correctamente.')

        except Exception as e:
            messages.error(request, f'Error al eliminar el producto de la cesta: {str(e)}')
    else:
        messages.error(request, 'El producto no está en la cesta.')

    return redirect('ver_carrito')

def actualizar_cantidad(request, producto_id, cambio):

    user = request.user
    uid = obtener_uid(request)

    if hasattr(user, 'productor'):
        user = user.productor

    if(isinstance(user, Productor)):
        user_ref = database.child("Productores").child(uid)
    else:
        user_ref = database.child("Consumidores").child(uid)

    user_data = user_ref.get().val()

    try:
        cambio = int(cambio)
    except ValueError:
        messages.error(request, 'Cambio inválido.')
        return redirect('ver_carrito')

    if user_data and 'carrito' in user_data and producto_id in user_data['carrito']:
        try:
            nueva_cantidad = user_data['carrito'][producto_id]['cantidad'] + cambio

            if nueva_cantidad < 1:
                messages.error(request, 'No se puede establecer una cantidad menor que 1.')
                return redirect('ver_carrito')

            if(isinstance(user, Productor)):
                database.child("Productores").child(uid).child('carrito').child(producto_id).child('cantidad').set(nueva_cantidad)
            else:
                database.child("Consumidores").child(uid).child('carrito').child(producto_id).child('cantidad').set(nueva_cantidad)

        except Exception as e:
            messages.error(request, f'Error al actualizar la cantidad del producto: {e}')

    return redirect('ver_carrito')

def vaciar_carrito(request):
    
    user = request.user
    uid = obtener_uid(request)

    if hasattr(user, 'productor'):
        user = user.productor

    if(isinstance(user, Productor)):
        user_ref = database.child("Productores").child(uid)
    else:
        user_ref = database.child("Consumidores").child(uid)

    user_data = user_ref.get().val()

    if user_data and 'carrito' in user_data:
        try:
            if(isinstance(user, Productor)):
                database.child("Productores").child(uid).child('carrito').remove()
            else:
                database.child("Consumidores").child(uid).child('carrito').remove()
            messages.success(request, 'La cesta se ha vaciado correctamente.')

        except Exception as e:
            messages.error(request, f'Error al vaciar la cesta: {str(e)}')
    else:
        messages.error(request, 'No hay productos en la cesta.')
        
    return redirect('ver_carrito')

def checkout(request):
    if request.method == 'POST':
        # Crear una sesión de pago
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Nombre del Producto',
                    },
                    'unit_amount': 1000,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=settings.DOMAIN_URL + '/payment_success/',
            cancel_url=settings.DOMAIN_URL + '/payment_cancel/',
        )
        return redirect(session.url, code=303)
    return render(request, 'checkout.html', {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    })

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_cancel(request):
    return render(request, 'payment_cancel.html')




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