from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Vecino(AbstractUser):
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    verificado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # 🔧 Evita conflicto con el modelo User de Django
    groups = models.ManyToManyField(
        Group,
        related_name='vecinos_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='vecinos_set',
        blank=True
    )

    class Meta:
        db_table = 'vecinos'
        verbose_name = 'Vecino'
        verbose_name_plural = 'Vecinos'
    
    def __str__(self):
        return f"{self.username} - {self.direccion}"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
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
    autor = models.ForeignKey(Vecino, on_delete=models.CASCADE)
    categorias = models.ManyToManyField(Categoria, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fijado = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'publicaciones'
        ordering = ['-fecha_creacion']
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'
    
    def __str__(self):
        return f"{self.titulo} - {self.autor.username}"


class Comentario(models.Model):
    contenido = models.TextField()
    autor = models.ForeignKey(Vecino, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    fecha_comentario = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comentarios'
        ordering = ['fecha_comentario']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
    
    def __str__(self):
        return f"Comentario de {self.autor.username}"


class Reaccion(models.Model):
    TIPO_CHOICES = [
        ('LIKE', '👍'),
        ('DISLIKE', '👎'),
        ('CORAZON', '❤️'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='LIKE')
    vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    fecha_reaccion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reacciones'
        unique_together = ['vecino', 'publicacion']
        verbose_name = 'Reacción'
        verbose_name_plural = 'Reacciones'
    
    def __str__(self):
        return f"{self.tipo} - {self.vecino.username}"
