from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Publicacion, Vecino, Comentario
from .forms import RegistroForm, LoginForm, PublicacionForm, ComentarioForm
from django.contrib.auth import get_user_model

from django.shortcuts import render, redirect, get_object_or_404
from .models import Publicacion, Vecino, Comentario
from django.contrib.auth.decorators import user_passes_test
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import Group


def es_moderador(user):
    return user.groups.filter(name="Moderador").exists()


def feed_principal(request):
    publicaciones = Publicacion.objects.filter(
        aprobada=True,
        visible=True
    ).order_by('-fecha_creacion')

    return render(request, 'feed.html', {
        'publicaciones': publicaciones
    })



from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.shortcuts import redirect, render

def login_view(request):
    """Vista para iniciar sesión"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        User = get_user_model()

        try:
            u = User.objects.get(username=username)
            if not u.is_active:
                messages.error(request, "Tu cuenta ha sido baneada. Contacta al administrador.")
                return render(request, 'login.html', {'form': form})
        except User.DoesNotExist:
            pass 


        if form.is_valid():
            user = authenticate(request, username=username, password=password)

            if user is None:
                messages.error(request, "Credenciales inválidas.")
                return render(request, 'login.html', {'form': form})

            login(request, user)
            messages.success(request, f'¡Bienvenido de vuelta, {username}!')
            return redirect('app:feed')

       
        messages.error(request, "Credenciales inválidas.")
        return render(request, 'login.html', {'form': form})

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

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
    if request.method == 'POST':
        form = PublicacionForm(request.POST)

        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user

            # Evaluamos permisos correctamente
            if request.user.is_superuser or es_moderador(request.user):
                publicacion.aprobada = True
                mensaje = "Publicación creada y aprobada automáticamente."
            else:
                publicacion.aprobada = False
                mensaje = "Tu publicación ha sido enviada para revisión."

            publicacion.save()
            form.save_m2m()

            messages.success(request, mensaje)
            return redirect('app:feed')

    else:
        form = PublicacionForm()

    return render(request, 'crear_publicacion.html', {
        'form': form,
        'es_moderador': es_moderador(request.user),
    })




def prueba(request):
    return HttpResponse("¡PRUEBA EXITOSA! 🎉")


@login_required
def detalle_publicacion(request, id):
    publicacion = get_object_or_404(Publicacion, id=id)

    
    comentarios = Comentario.objects.filter(
        publicacion=publicacion
    ).order_by('-fecha_comentario')

    if request.method == "POST":
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.autor = request.user
            comentario.publicacion = publicacion
            comentario.save()
            return redirect('app:detalle_publicacion', id=id)
    else:
        form = ComentarioForm()

    return render(request, 'detalle_publicacion.html', {
        'publicacion': publicacion,
        'comentarios': comentarios,
        'form': form,
    })


@login_required
def eliminar_publicacion(request, id):
    publicacion = get_object_or_404(Publicacion, id=id)

    # Permisos:
    # - Admin -> puede eliminar todo
    # - Moderador -> puede eliminar todo
    # - Usuario normal -> solo lo suyo
    if not (
        request.user.is_superuser or 
        es_moderador(request.user) or 
        request.user == publicacion.autor
    ):
        messages.error(request, "No tienes permiso para eliminar esta publicación.")
        return redirect('app:feed')

    if request.method == 'POST':
        publicacion.delete()
        messages.success(request, "Publicación eliminada correctamente.")
        return redirect('app:feed')

    return render(request, 'confirmar_eliminar.html', {'publicacion': publicacion})



@login_required
def editar_publicacion(request, id):
    publicacion = get_object_or_404(Publicacion, id=id)

    # Solo admin y moderador pueden editar
    if not (request.user.is_superuser or es_moderador(request.user)):
        messages.error(request, "No tienes permiso para editar publicaciones.")
        return redirect('app:feed')

    if request.method == 'POST':
        form = PublicacionForm(request.POST, instance=publicacion)
        if form.is_valid():
            form.save()
            messages.success(request, "Publicación actualizada exitosamente.")
            return redirect('app:detalle_publicacion', id=publicacion.id)
    else:
        form = PublicacionForm(instance=publicacion)

    return render(request, 'editar_publicacion.html', {'form': form, 'publicacion': publicacion})


@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    User = get_user_model()

    publicaciones = Publicacion.objects.order_by('-fecha_creacion')[:20]

    usuarios_qs = User.objects.prefetch_related('groups').order_by('-date_joined')

    moderadores_ids = set(
        usuarios_qs.filter(groups__name="Moderador").values_list('id', flat=True)
    )

    # ✔ mostramos solo los 20 últimos
    usuarios = usuarios_qs[:20]

    return render(request, "admin_panel.html", {
        "usuarios": usuarios,
        "publicaciones": publicaciones,
        "moderadores_ids": moderadores_ids,
        "denuncias": [],
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_publicacion_eliminar(request, pk):
    """Eliminar una publicación desde el panel admin"""
    pub = get_object_or_404(Publicacion, pk=pk)
    if request.method == 'POST':
        pub.delete()
        messages.success(request, 'Publicación eliminada.')
        return redirect('app:admin_panel')
    # Si quieres confirmación con plantilla, puedes renderizarla;
    # si no, eliminamos solo con POST y listo.
    return redirect('app:admin_panel')


@user_passes_test(lambda u: u.is_superuser)
def admin_publicacion_toggle(request, pk):
    """
    Ocultar/mostrar (toggle) una publicación si tu modelo tiene un booleano como
    'visible' o 'activo'. Ajusta a tu campo real.
    """
    pub = get_object_or_404(Publicacion, pk=pk)

    # Intenta detectar campo común:
    if hasattr(pub, 'visible'):
        pub.visible = not pub.visible
    elif hasattr(pub, 'activo'):
        pub.activo = not pub.activo
    else:
        messages.warning(request, 'No existe un campo visible/activo para alternar estado.')
        return redirect('app:admin_panel')

    pub.save()
    messages.success(request, 'Estado de la publicación actualizado.')
    return redirect('app:admin_panel')

@user_passes_test(lambda u: u.is_superuser)
def admin_eliminar_usuario(request, user_id):
    User = get_user_model()
    usuario = get_object_or_404(User, id=user_id)

    # Seguridad: no borrar superusers
    if usuario.is_superuser:
        messages.error(request, "No puedes eliminar un administrador.")
        return redirect('app:admin_panel')

    # Seguridad: no permitir borrarse a uno mismo
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect('app:admin_panel')

    usuario.delete()
    messages.success(request, f"Usuario {usuario.username} eliminado correctamente.")
    return redirect('app:admin_panel')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_toggle_moderador(request, user_id):
    User = get_user_model()
    usuario = get_object_or_404(User, id=user_id)

    # Evitar tocar superusers por seguridad
    if usuario.is_superuser:
        messages.warning(request, "No puedes cambiar el rol de un administrador.")
        return redirect('app:admin_panel')

    grupo_moderador, _ = Group.objects.get_or_create(name="Moderador")

    if grupo_moderador in usuario.groups.all():
        usuario.groups.remove(grupo_moderador)
        messages.success(request, f"Se quitó el rol de moderador a {usuario.username}.")
    else:
        usuario.groups.add(grupo_moderador)
        messages.success(request, f"{usuario.username} ahora es moderador.")

    return redirect('app:admin_panel')


@login_required
@user_passes_test(lambda u: u.is_superuser or es_moderador(u))
def moderar_publicaciones(request):
    pendientes = Publicacion.objects.filter(estado='PENDIENTE')

    return render(request, 'moderar_publicaciones.html', {
        'pendientes': pendientes
    })


@login_required
@user_passes_test(lambda u: u.is_superuser or es_moderador(u))
def rechazar_publicacion(request, id):
    pub = get_object_or_404(Publicacion, id=id)
    pub.delete()

    messages.info(request, 'Publicación rechazada y eliminada.')
    return redirect('app:moderar_publicaciones')

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404, redirect
from .models import Publicacion

def es_moderador(user):
    return user.groups.filter(name='Moderador').exists()

@login_required
def panel_moderador(request):
    if not es_moderador(request.user) and not request.user.is_superuser:
        messages.error(request, "No tienes permisos de moderador.")
        return redirect('app:feed')

    User = get_user_model()

    pendientes = Publicacion.objects.filter(aprobada=False)
    aprobadas = Publicacion.objects.filter(aprobada=True)
    usuarios = User.objects.order_by('-date_joined')[:50]  # los últimos 50

    return render(request, "panel_moderador.html", {
        "pendientes": pendientes,
        "aprobadas": aprobadas,
        "usuarios": usuarios,
    })



@login_required
def moderador_toggle_visible(request, pk):
    pub = get_object_or_404(Publicacion, pk=pk)

    if not es_moderador(request.user) and not request.user.is_superuser:
        return redirect('app:index')

    pub.visible = not pub.visible
    pub.save()
    return redirect('app:panel_moderador')


@login_required
def moderador_eliminar(request, pk):
    pub = get_object_or_404(Publicacion, pk=pk)

    if not es_moderador(request.user) and not request.user.is_superuser:
        return redirect('app:index')

    pub.delete()
    return redirect('app:panel_moderador')

@login_required
def aprobar_publicacion(request, id):
    if not (request.user.is_superuser or es_moderador(request.user)):
        messages.error(request, "No tienes permiso para aprobar publicaciones.")
        return redirect('app:feed')

    publicacion = get_object_or_404(Publicacion, id=id)

    publicacion.aprobada = True 
    publicacion.visible = True    
    publicacion.save()

    messages.success(request, "Publicación aprobada correctamente.")
    return redirect('app:panel_moderador')

@login_required
def moderador_toggle_ban(request, user_id):
    User = get_user_model()
    usuario = get_object_or_404(User, id=user_id)

    # No permitir banear a administradores
    if usuario.is_superuser:
        messages.error(request, "No puedes banear a un administrador.")
        return redirect('app:panel_moderador')

    # No permitir banearse a sí mismo
    if usuario == request.user:
        messages.error(request, "No puedes banear tu propia cuenta.")
        return redirect('app:panel_moderador')

    # Alternar estado de is_active
    usuario.is_active = not usuario.is_active
    usuario.save()

    if usuario.is_active:
        messages.success(request, f"Usuario {usuario.username} desbaneado.")
    else:
        messages.success(request, f"Usuario {usuario.username} baneado.")

    return redirect('app:panel_moderador')


@login_required
def crear_comentario(request, id):
    publicacion = get_object_or_404(Publicacion, id=id)

    # NO permitimos que el admin comente
    if request.user.is_superuser:
        messages.error(request, "El administrador no puede comentar.")
        return redirect('app:detalle_publicacion', id=id)

    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()

        if contenido == "":
            messages.error(request, "El comentario no puede estar vacío.")
            return redirect('app:detalle_publicacion', id=id)

        Comentario.objects.create(
            contenido=contenido,
            autor=request.user,
            publicacion=publicacion
        )

        messages.success(request, "Comentario publicado.")
        return redirect('app:detalle_publicacion', id=id)

    # No permitimos GET (solo POST)
    return redirect('app:detalle_publicacion', id=id)

@login_required
def crear_alerta(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()

        if titulo == "" or descripcion == "":
            messages.error(request, "Debes completar todos los campos.")
            return redirect("app:crear_alerta")

        Publicacion.objects.create(
            titulo=titulo,
            contenido=descripcion,
            tipo="ALERTA",   
            autor=request.user,
            aprobada=True,   
            visible=True    
        )

        messages.success(request, "🚨 Alerta publicada correctamente.")
        return redirect("app:feed")

    return render(request, "crear_alerta.html")

