# Compras/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Apps.Usuarios.models import Consumidor, Productor
from django.conf import settings
import firebase_admin
from firebase_admin import credentials, auth, storage, initialize_app

from datetime import datetime
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

    productores_ref = database.child("Productores").get()
    producto_data = None

    # Recorrer cada productor y obtener el producto
    for productor in productores_ref.each():
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

        # aumentamos la cantidad en la cesta y se disminuye de la bbdd
        for productor in productores_ref.each():
            productos_productor = productor.val().get('productos', {})
            if producto_id in productos_productor:
                # Decrementar el stock
                stock_actual = productos_productor[producto_id].get('stock', 0)
                nuevo_stock = stock_actual - 1

                if nuevo_stock < 0:
                    messages.error(request, 'No hay más productos en stock')
                    return redirect('list_products')
                else:
                    # Actualizar el stock en la base de datos
                    database.child("Productores").child(productor.key()).child('productos').child(producto_id).update({'stock': nuevo_stock})
                    messages.success(request, f'{producto_data["nombre"]} añadido con éxito a la cesta')
        
        # Actualizar el carrito en la base de datos
        if(isinstance(user, Productor)):
            database.child("Productores").child(uid).child('carrito').set(carrito_actual)
        else:
            database.child("Consumidores").child(uid).child('carrito').set(carrito_actual)

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
            cantidad_en_carrito = user_data['carrito'][producto_id]['cantidad']

            if(isinstance(user, Productor)):
                database.child("Productores").child(uid).child('carrito').child(producto_id).remove()
            else:
                database.child("Consumidores").child(uid).child('carrito').child(producto_id).remove()
            messages.success(request, 'Producto eliminado de la cesta correctamente.')

            productores_ref = database.child("Productores").get()

            # Aumentar el stock del producto eliminado en todos los productores
            for productor in productores_ref.each():
                productos_productor = productor.val().get('productos', {})
                if producto_id in productos_productor:
                    stock_actual = productos_productor[producto_id].get('stock', 0)
                    nuevo_stock = stock_actual + cantidad_en_carrito
                    database.child("Productores").child(productor.key()).child('productos').child(producto_id).update({'stock': nuevo_stock})

        except Exception as e:
            messages.error(request, f'Error al eliminar el producto de la cesta: {str(e)}')
    else:
        messages.error(request, 'El producto no está en la cesta.')

    return redirect('ver_carrito')

@login_required
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

            productores_ref = database.child("Productores").get()
            # aumentamos la cantidad en la cesta y se disminuye de la bbdd
            for productor in productores_ref.each():
                productos_productor = productor.val().get('productos', {})
                if producto_id in productos_productor:
                    # Decrementar el stock
                    stock_actual = productos_productor[producto_id].get('stock', 0)
                    nuevo_stock = stock_actual - cambio

                    if nuevo_stock < 0:
                        messages.error(request, 'No hay más productos en stock')
                        return redirect('ver_carrito')
                    else:
                        database.child("Productores").child(productor.key()).child('productos').child(producto_id).update({'stock': nuevo_stock})
                        if cambio > 0:
                            messages.success(request, f'Producto añadido con éxito a la cesta')
                        elif nueva_cantidad > 0:
                            messages.success(request, f'Producto eliminado con éxito de la cesta')
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

@login_required
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
            # Recuperar el carrito actual
            carrito_actual = user_data['carrito']

            productores_ref = database.child("Productores").get()

            for productor in productores_ref.each():
                productos_productor = productor.val().get('productos', {})

                for producto_id, producto in carrito_actual.items():
                    if producto_id in productos_productor:
                        cantidad_en_carrito = producto['cantidad']
                        stock_actual = productos_productor[producto_id].get('stock', 0)
                        nuevo_stock = stock_actual + cantidad_en_carrito

                        # Actualizar el stock en la base de datos
                        database.child("Productores").child(productor.key()).child('productos').child(producto_id).update({'stock': nuevo_stock})

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

@login_required
def checkout(request):

    user = request.user
    uid = obtener_uid(request)
    
    if hasattr(user, 'productor'):
        user = user.productor

    if isinstance(user, Productor):
        user_ref = database.child("Productores").child(uid)
    else:
        user_ref = database.child("Consumidores").child(uid)

    user_data = user_ref.get().val()
    carrito_actual = user_data.get('carrito', {})
    cesta_items = []

    for productoid, producto in carrito_actual.items():
        
        cesta_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': producto.get('nombre'),
                },
                'unit_amount': int(producto.get('precio') * 100),
            },
            'quantity': producto.get('cantidad'),
        })

    if request.method == 'POST':
        # Crear sesión de Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=cesta_items,
            mode='payment',
            success_url=settings.DOMAIN_URL + '/payment_success/',
            cancel_url=settings.DOMAIN_URL + '/payment_cancel/',
            shipping_address_collection={
                'allowed_countries': ['ES'],
            },
            shipping_options=[
                {
                    'shipping_rate_data': {
                        'type': 'fixed_amount',
                        'fixed_amount': {'amount': 0, 'currency': 'eur'},
                        'display_name': 'Envío estándar',
                        'delivery_estimate': {
                            'minimum': {'unit': 'business_day', 'value': 5},
                            'maximum': {'unit': 'business_day', 'value': 7},
                        },
                    },
                },
            ],
        )
        return redirect(session.url, code=303)

    total = sum(producto.get('precio') * producto.get('cantidad') for productoid, producto in carrito_actual.items())

    return render(request, 'checkout.html', {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'carrito': carrito_actual,
        'total': total
    })

def payment_success(request):

    user = request.user
    uid = obtener_uid(request)

    if hasattr(user, 'productor'):
        user = user.productor

    if(isinstance(user, Productor)):
        user_ref = database.child("Productores").child(uid)
    else:
        user_ref = database.child("Consumidores").child(uid)

    user_data = user_ref.get().val()
    direccion = user_data.get('direccion', '')

    if user_data and 'carrito' in user_data:
        try:
            # Recuperar el carrito actual
            carrito_actual = user_data['carrito']

            # Añadir campo 'valorado: False' a cada producto en el carrito
            for producto_id, producto in carrito_actual.items():
                producto['valorado'] = False
            
            precio_total = sum(item['precio'] * item['cantidad'] for item in carrito_actual.values())
            fecha_compra = datetime.now().strftime('%d/%m/%Y %H:%M')
                
            if(isinstance(user, Productor)):
                # Obtener el número de compra actual
                compras = user_data.get('compras', {})
                numero_compra = len(compras) + 1

                # Añadir compra a la base de datos
                nueva_compra = {
                    'carrito': carrito_actual,
                    'fecha': fecha_compra,
                    'precio_total': precio_total,
                    'numero_compra': numero_compra,
                    'direccion': direccion
                }
                database.child("Productores").child(uid).child('compras').child(f'compra_{numero_compra}').set(nueva_compra)
                database.child("Productores").child(uid).child('carrito').remove()
            else:
                # Obtener el número de compra actual
                compras = user_data.get('compras', {})
                numero_compra = len(compras) + 1

                # Añadir compra a la base de datos
                nueva_compra = {
                    'carrito': carrito_actual,
                    'fecha': fecha_compra,
                    'precio_total': precio_total,
                    'numero_compra': numero_compra
                }
                database.child("Consumidores").child(uid).child('compras').child(f'compra_{numero_compra}').set(nueva_compra)
                database.child("Consumidores").child(uid).child('carrito').remove()
            
            print(f'compra añadida a la BBDD correctamente')

        except Exception as e:
            messages.error(request, f'Ha habido un error: {str(e)}')
    else:
        messages.error(request, 'No hay productos en la cesta.')


    return render(request, 'pagado.html')

def payment_cancel(request):
    return render(request, 'pago_cancelado.html')

@login_required
def mis_compras(request):
    user = request.user
    uid = obtener_uid(request)
    
    if hasattr(user, 'productor'):
        user = user.productor

    if(isinstance(user, Productor)):
        user_ref = database.child("Productores").child(uid)
    else:
        user_ref = database.child("Consumidores").child(uid)

    user_data = user_ref.get().val()
    compras_actual = user_data.get('compras', {})

    total_compras = 0
    productos = []

    # Itera sobre las compras
    for compra_id, compra in compras_actual.items():
        total_compras += compra.get('precio_total', 0)
        for product_id, producto in compra.get('carrito', {}).items():
            productos.append(producto)

    context = {
        'mis_compras': compras_actual,
        'total': total_compras,
        'range': range(5, 0, -1),
        'productos': productos
    }

    return render(request, "mis_compras.html", context)

@login_required
def valorar_producto(request):
    if request.method == 'POST':

        user = request.user
        uid = obtener_uid(request)

        producto_id = request.POST.get('producto_id')
        valoracion_nueva = int(request.POST.get('valoracion'))

        try:

            productores_ref = database.child("Productores").get()

            # Valoración del producto buscándolo de entre todos los productores
            for productor in productores_ref.each():
                productos_productor = productor.val().get('productos', {})
                if producto_id in productos_productor:
                    valoraciones_actual = productos_productor[producto_id].get("valoraciones", 0)
                    valoracion_total_actual = productos_productor[producto_id].get("valoracion", 0)
                    
                    valoraciones_nueva = valoraciones_actual + 1
                    valoracion_media = (valoracion_total_actual * valoraciones_actual + valoracion_nueva) / valoraciones_nueva
                
                    database.child("Productores").child(productor.key()).child('productos').child(producto_id).update({
                            'valoracion': valoracion_media,
                            'valoraciones': valoraciones_nueva
                        })

                    # actualizar valorado a true
                    if(isinstance(user, Productor)):
                        user_ref = database.child("Productores").child(uid)
                    else:
                        user_ref = database.child("Consumidores").child(uid)

                        user_data = user_ref.get().val()
                        compras_actual = user_data.get('compras', {})

                        # Itera sobre las compras
                        for compra_id, compra in compras_actual.items():
                            carrito_nuevo  = compra.get('carrito', {})
                            carrito_actual = compra.get('carrito', {})
  
                            if producto_id in carrito_actual:
                                carrito_nuevo[producto_id]['valorado'] = True
                                print(carrito_actual)

                                if(isinstance(user, Productor)):
                                    database.child("Productores").child(uid).child('compras').child(compra_id).child('carrito').update(carrito_nuevo)
                                else:
                                    database.child("Consumidores").child(uid).child('compras').child(compra_id).child('carrito').update(carrito_nuevo)

                
            messages.success(request, 'Valoración aportada correctamente.')                            

        except Exception as e:
            messages.error(request, f'El producto no existe: {str(e)}')
            print(e)

    return redirect('/usuarios/mis_compras')

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