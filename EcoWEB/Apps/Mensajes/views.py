from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversacion, Mensaje
from Apps.Usuarios.models import Consumidor
from django.utils import timezone
from django.urls import reverse

@login_required
def lista_conversaciones(request):
    usuario = request.user
    conversaciones = Conversacion.objects.filter(participante1=usuario) | Conversacion.objects.filter(participante2=usuario)
    return render(request, 'lista_conversaciones.html', {'conversaciones': conversaciones})

@login_required
def ver_conversacion(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    mensajes = conversacion.mensajes.order_by('fecha_envio')
    return render(request, 'ver_conversacion.html', {'conversacion': conversacion, 'mensajes': mensajes})

@login_required
def enviar_mensaje(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        if contenido:
            mensaje = Mensaje(conversacion=conversacion, emisor=request.user, contenido=contenido)
            mensaje.save()
            conversacion.ultimo_mensaje = contenido
            conversacion.fecha_ultimo_mensaje = timezone.now()
            conversacion.save()
            return redirect('ver_conversacion', conversacion_id=conversacion.id)
    return render(request, 'enviar_mensaje.html', {'conversacion': conversacion})

@login_required
def iniciar_conversacion(request, usuario_id):
    try:
        # Obtener el usuario destinatario
        destinatario = Consumidor.objects.get(id=usuario_id)
        
        # Verificar si ya existe una conversación entre el usuario actual y el destinatario
        conversacion_existente = Conversacion.objects.filter(participante1=request.user, participante2=destinatario) | Conversacion.objects.filter(participante1=destinatario, participante2=request.user)
        
        if conversacion_existente.exists():
            # Si la conversación ya existe, redirigir a ver_conversacion.html
            conversacion = conversacion_existente.first()
            return redirect(reverse('ver_conversacion', args=[conversacion.id]))
        else:
            # Si no existe, crear una nueva conversación
            nueva_conversacion = Conversacion.objects.create(participante1=request.user, participante2=destinatario)
            return redirect(reverse('ver_conversacion', args=[nueva_conversacion.id]))
    
    except Consumidor.DoesNotExist:
        print("No existe el consumidor")
        return redirect('/usuarios/productores/')

    except Exception as e:
        print(e)
        return redirect('/usuarios/productores/')