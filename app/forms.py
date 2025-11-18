from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Vecino, Publicacion, Categoria

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'tu@email.com'
    }))
    direccion = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Tu dirección (opcional)'
    }))
    telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Tu teléfono (opcional)'
    }))

    class Meta:
        model = Vecino
        fields = ['username', 'email', 'password1', 'password2', 'direccion', 'telefono']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases Bootstrap a todos los campos
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases Bootstrap a todos los campos
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['titulo', 'contenido', 'tipo', 'categorias']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de tu publicación'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu publicación aquí...',
                'rows': 4
            }),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'categorias': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
    
    def clean_titulo(self):
        titulo = self.cleaned_data['titulo'].strip()
        if len(titulo) < 5:
            raise ValidationError("El título debe tener al menos 5 caracteres")
        return titulo
    
    def clean_contenido(self):
        contenido = self.cleaned_data['contenido'].strip()
        if len(contenido) < 10:
            raise ValidationError("El contenido debe tener al menos 10 caracteres")
        return contenido