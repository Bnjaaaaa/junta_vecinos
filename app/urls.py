from django.urls import path
from . import views
from .views import detalle_publicacion

app_name = 'app'

urlpatterns = [

    # ---- FEED ----
    path('', views.feed_principal, name='feed'),

    # ---- AUTENTICACIÓN ----
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # ---- PUBLICACIONES ----
    path('publicar/', views.crear_publicacion, name='crear_publicacion'),
    path('publicacion/<int:id>/', detalle_publicacion, name='detalle_publicacion'),
    path('publicacion/<int:id>/editar/', views.editar_publicacion, name='editar_publicacion'),

    # ---- PANEL ADMIN ----
    path('admin/panel/', views.admin_panel, name='admin_panel'),
    path('admin/publicacion/<int:pk>/eliminar/', views.admin_publicacion_eliminar, name='admin_publicacion_eliminar'),
    path('admin/publicacion/<int:pk>/toggle/', views.admin_publicacion_toggle, name='admin_publicacion_toggle'),

    # ---- PANEL MODERADOR ----
    path('moderador/', views.panel_moderador, name='panel_moderador'),
    path('moderador/publicacion/<int:pk>/toggle/', views.moderador_toggle_visible, name='moderador_toggle'),
    path('moderador/publicacion/<int:pk>/eliminar/', views.moderador_eliminar, name='moderador_eliminar'),
    path('moderador/aprobar/<int:id>/', views.aprobar_publicacion, name='aprobar_publicacion'),

    # ---- PRUEBA ----
    path('prueba/', views.prueba, name='prueba'),
]
