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
    path('publicacion/<int:id>/eliminar/', views.eliminar_publicacion, name='eliminar_publicacion'),


    # ---- PANEL ADMIN ----
    path('admin/panel/', views.admin_panel, name='admin_panel'),
    path('admin/publicacion/<int:pk>/eliminar/', views.admin_publicacion_eliminar, name='admin_publicacion_eliminar'),
    path('admin/publicacion/<int:pk>/toggle/', views.admin_publicacion_toggle, name='admin_publicacion_toggle'),
    path('admin/usuario/<int:user_id>/toggle-moderador/', views.admin_toggle_moderador, name='admin_toggle_moderador'),
    path('admin/usuario/<int:user_id>/eliminar/', views.admin_eliminar_usuario, name='admin_eliminar_usuario'),



    # ---- PANEL MODERADOR ----
    path('moderador/', views.panel_moderador, name='panel_moderador'),
    path('moderador/publicacion/<int:pk>/toggle/', views.moderador_toggle_visible, name='moderador_toggle'),
    path('moderador/publicacion/<int:pk>/eliminar/', views.moderador_eliminar, name='moderador_eliminar'),
    path('moderador/aprobar/<int:id>/', views.aprobar_publicacion, name='aprobar_publicacion'),
    path('moderador/usuario/<int:user_id>/toggle-ban/', views.moderador_toggle_ban, name='moderador_toggle_ban'),

    # ---- COMENTARIOS ----
    path('publicacion/<int:id>/comentar/', views.crear_comentario, name='crear_comentario'),

    # ---- ALERTA ----
    path('alerta/', views.crear_alerta, name='crear_alerta'),



    # ---- PRUEBA ----
    path('prueba/', views.prueba, name='prueba'),
]
