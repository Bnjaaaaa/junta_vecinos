from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.conf import settings

# ======================================
# 🌟 USUARIO PERSONALIZADO (VECINO)
# ======================================
class Vecino(AbstractUser):
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    verificado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vecinos'
        verbose_name = 'Vecino'
        verbose_name_plural = 'Vecinos'

    def __str__(self):
        return f"{self.username} - {self.direccion if self.direccion else 'Sin dirección'}"


# ======================================
# 🌟 CATEGORÍAS
# ======================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Publicacion(models.Model):
    TIPO_CHOICES = [
        ('ALERTA', '⚠️ Alerta'),
        ('EVENTO', '📅 Evento'),
        ('RECOMENDACION', '💡 Recomendación'),
        ('PREGUNTA', '❓ Pregunta'),
    ]

    titulo = models.CharField(max_length=150)
    contenido = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='RECOMENDACION')

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publicaciones'
    )

    categorias = models.ManyToManyField(Categoria, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    fijado = models.BooleanField(default=False)

    # ✔ necesario para admin_publicacion_toggle()
    visible = models.BooleanField(default=True)

    # ✔ NUEVO: aprobación por moderador/admin
    aprobada = models.BooleanField(default=False)

    class Meta:
        db_table = 'publicaciones'
        ordering = ['-fecha_creacion']
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'

    def __str__(self):
        return f"{self.titulo} - {self.autor.username}"



# ======================================
# 🌟 COMENTARIOS
# ======================================
class Comentario(models.Model):
    contenido = models.TextField()
    
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )

    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )

    fecha_comentario = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comentarios'
        ordering = ['fecha_comentario']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f"Comentario de {self.autor.username}"


# ======================================
# 🌟 REACCIONES
# ======================================
class Reaccion(models.Model):
    TIPO_CHOICES = [
        ('LIKE', '👍'),
        ('DISLIKE', '👎'),
        ('CORAZON', '❤️'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='LIKE')

    vecino = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reacciones'
    )

    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='reacciones'
    )

    fecha_reaccion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reacciones'
        unique_together = ['vecino', 'publicacion']
        verbose_name = 'Reacción'
        verbose_name_plural = 'Reacciones'

    def __str__(self):
        return f"{self.tipo} - {self.vecino.username}"
