"""
URL configuration for EcoWEB project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from EcoWEB import views as ecoweb_views

from Apps.Usuarios import views as usuarios_views
from Apps.Productos import views as productos_views
from Apps.Compras import views as carrito_views
from Apps.Mensajes import views as mensajes_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # path('', ecoweb_views.home, name='index'),
    path('', ecoweb_views.mostrar_mejores_productos, name='index'),

    ################################################################################################# 

    ########################################### USUARIOS ############################################
    
    path('usuarios/login/', usuarios_views.log_in, name='login'),
    path('accounts/signup/', usuarios_views.signup_consumidor),
    path('accounts/login/', usuarios_views.log_in),
    path("accounts/", include("allauth.urls")),
    path('usuarios/signup/', usuarios_views.signup_consumidor, name='signup_consumidor'),
    path('usuarios/signup_prod/', usuarios_views.signup_productor, name='signup_productor'),
    path('usuarios/signup/logout/', usuarios_views.log_out),
    path('usuarios/firebase_register/', usuarios_views.firebase_register),

    path('usuarios/password_reset/', usuarios_views.CustomPasswordResetView.as_view(template_name='password_reset_form.html', email_template_name='password_reset_email.html'), name='password_reset'),
    path('usuarios/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('usuarios/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('usuarios/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    path('usuarios/send_mail/', usuarios_views.enviar_mail),
    
    path('usuarios/perfil/', usuarios_views.perfil, name='perfil'),
    path('usuarios/editar_perfil/', usuarios_views.edit_profile, name='edit_profile'),
    path('usuarios/editar_perfil_prod/', usuarios_views.edit_profile_prod, name='edit_profile_prod'),
    path('usuarios/productores/', usuarios_views.muestra_productores, name='productores'),
    path('usuarios/eliminar/', usuarios_views.eliminar_usuario, name='eliminar_user'),

    path('usuarios/mis_compras', carrito_views.mis_compras, name='mis_compras'),

    ################################################################################################# 

    ########################################### PRODUCTOS ###########################################

    path('productos/', productos_views.products, name='products'),
    path('detalle_producto/<str:producto_id>/', productos_views.detalle_producto, name='detalle_producto'),
    path('usuarios/productos/add/', productos_views.add_product, name='add_product'),
    path('usuarios/productos/edit/<str:product_id>/', productos_views.edit_product, name='edit_product'),
    path('usuarios/productos/delete/<str:product_id>/', productos_views.delete_product, name='delete_product'),
    path('productos/lista_productos/', productos_views.lista_productos, name='list_products'),

    path('usuarios/productos/valorar_producto/', carrito_views.valorar_producto, name='valorar_producto'),

    ################################################################################################# 

    ############################################ COMPRAS ############################################

    path('carrito/', carrito_views.ver_carrito, name='ver_carrito'),
    path('carrito/add_carrito/<str:producto_id>/', carrito_views.add_carrito, name='add_carrito'),
    path('carrito/eliminar/<str:producto_id>/', carrito_views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
    path('carrito/actualizar/<str:producto_id>/<str:cambio>/', carrito_views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/vaciar/', carrito_views.vaciar_carrito, name='vaciar_carrito'),

    path('checkout/', carrito_views.checkout, name='checkout'),
    path('payment_success/', carrito_views.payment_success, name='pagado'),
    path('payment_cancel/', carrito_views.payment_cancel, name='pago_cancelado'),

    ################################################################################################# 

    ########################################### MENSAJES ############################################

      path('mensajes/lista_conversaciones/', mensajes_views.lista_conversaciones, name='lista_conversaciones'),
      path('mensajes/ver_conversacion/<int:conversacion_id>/', mensajes_views.ver_conversacion, name='ver_conversacion'),
      path('mensajes/enviar_mensaje/<int:conversacion_id>/', mensajes_views.enviar_mensaje, name='enviar_mensaje'),
      path('iniciar_conversacion/<int:usuario_id>/', mensajes_views.iniciar_conversacion, name='iniciar_conversacion'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
