from django.urls import path
from . import views

from . views import detalle_publicacion

app_name = 'app'

urlpatterns = [
    path('', views.feed_principal, name='feed'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('publicar/', views.crear_publicacion, name='crear_publicacion'),

    
    path('prueba/', views.prueba, name='prueba'),  # ← Agrega esta línea
    path('', views.feed_principal, name='feed'),

    path('publicacion/<int:id>/', detalle_publicacion, name='detalle_publicacion'),


]