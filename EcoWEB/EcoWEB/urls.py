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
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from EcoWEB import views as ecoweb_views

from Apps.Usuarios import views as usuarios_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', ecoweb_views.home, name='index'),
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


    path('usuarios/productos/', usuarios_views.products, name='products'),
    path('usuarios/lista_productos/', usuarios_views.lista_productos, name='list_products'),
    path('detalle_producto/<str:producto_id>/', usuarios_views.detalle_producto, name='detalle_producto'),
    path('usuarios/productos/add/', usuarios_views.add_product, name='add_product'),
    path('usuarios/productos/edit/<str:product_id>/', usuarios_views.edit_product, name='edit_product'),
    path('usuarios/productos/delete/<str:product_id>/', usuarios_views.delete_product, name='delete_product'),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
