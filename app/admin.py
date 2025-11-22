from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Vecino

@admin.register(Vecino)
class VecinoAdmin(UserAdmin):
    model = Vecino
    list_display = ('username', 'email', 'direccion', 'telefono', 'verificado', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ("Información adicional", {"fields": ("direccion", "telefono", "verificado")}),
    )
