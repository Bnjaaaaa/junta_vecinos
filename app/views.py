from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Publicacion, Vecino, Comentario
from .forms import RegistroForm, LoginForm, PublicacionForm

from django.shortcuts import render, redirect, get_object_or_404
from .models import Publicacion, Vecino, Comentario


def feed_principal(request):
    """Vista principal del feed de publicaciones"""
    publicaciones = Publicacion.objects.all().order_by('-fecha_creacion')
    
    contexto = {
        'publicaciones': publicaciones,
        'titulo_pagina': 'Feed Comunitario'
    }
    return render(request, 'feed.html', contexto)

def login_view(request):
    """Vista para iniciar sesión"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de vuelta, {username}!')
                return redirect('app:feed')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def registro_view(request):
    """Vista para registrar nuevos vecinos"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente! Bienvenido a la comunidad.')
            return redirect('app:feed')
    else:
        form = RegistroForm()
    
    return render(request, 'registro.html', {'form': form})

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('app:login')

@login_required
def crear_publicacion(request):
    """Vista para crear nuevas publicaciones (requiere login)"""
    if request.method == 'POST':
        form = PublicacionForm(request.POST)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            publicacion.save()
            form.save_m2m()  # Para las categorías ManyToMany
            messages.success(request, '¡Publicación creada exitosamente!')
            return redirect('app:feed')
    else:
        form = PublicacionForm()
    
    return render(request, 'crear_publicacion.html', {'form': form})

def prueba(request):
    return HttpResponse("¡PRUEBA EXITOSA! 🎉")


@login_required
def detalle_publicacion(request, id):
    # Obtener la publicación o mostrar 404 si no existe
    publicacion = get_object_or_404(Publicacion, id=id)

    # Obtener todos los comentarios relacionados
    comentarios = Comentario.objects.filter(publicacion=publicacion)

    return render(request, 'detalle_publicacion.html', {
        'publicacion': publicacion,
        'comentarios': comentarios
    })
