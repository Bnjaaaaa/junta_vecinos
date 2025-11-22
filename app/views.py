from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Publicacion, Vecino, Comentario
from .forms import RegistroForm, LoginForm, PublicacionForm
from django.contrib.auth import get_user_model

from django.shortcuts import render, redirect, get_object_or_404
from .models import Publicacion, Vecino, Comentario
from django.contrib.auth.decorators import user_passes_test
from django.db import models
from django.db.models import Q


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
    # Obtener la publicación o mostrar 404 si no existe
    publicacion = get_object_or_404(Publicacion, id=id)

    # Obtener todos los comentarios relacionados
    comentarios = Comentario.objects.filter(publicacion=publicacion)

    return render(request, 'detalle_publicacion.html', {
        'publicacion': publicacion,
        'comentarios': comentarios
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
    """
    Panel de administración:
    - Lista publicaciones (para gestionarlas)
    - Lista últimos usuarios (opcional)
    """
    User = get_user_model()

    
    publicaciones = (
        Publicacion.objects.select_related('autor')  # si el campo es 'autor'
        .order_by('-fecha_creacion')
    )

    usuarios = User.objects.order_by('-date_joined')[:20]

    contexto = {
        'publicaciones': publicaciones,
        'usuarios': usuarios,
        # Si luego agregas denuncias, las pasas aquí
        'denuncias': [],
    }
    return render(request, 'admin_panel.html', contexto)

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

@login_required
@user_passes_test(lambda u: u.is_superuser or es_moderador(u))
def moderar_publicaciones(request):
    pendientes = Publicacion.objects.filter(estado='PENDIENTE')

    return render(request, 'moderar_publicaciones.html', {
        'pendientes': pendientes
    })


@login_required
@user_passes_test(lambda u: u.is_superuser or es_moderador(u))
def aprobar_publicacion(request, id):
    pub = get_object_or_404(Publicacion, id=id)
    pub.estado = 'APROBADA'
    pub.save()

    messages.success(request, 'Publicación aprobada.')
    return redirect('app:moderar_publicaciones')



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

    pendientes = Publicacion.objects.filter(aprobada=False)
    aprobadas = Publicacion.objects.filter(aprobada=True)

    return render(request, "panel_moderador.html", {
        "pendientes": pendientes,
        "aprobadas": aprobadas,
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

    publicacion.aprobada = True   # ← FALTABA ESTO
    publicacion.visible = True    # ← Puedes dejarlo si quieres que se muestre de inmediato
    publicacion.save()

    messages.success(request, "Publicación aprobada correctamente.")
    return redirect('app:panel_moderador')

