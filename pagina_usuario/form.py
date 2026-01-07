from django import forms
from .models import DatosPersonales

class PerfilForm(forms.ModelForm):
    class Meta:
        model = DatosPersonales
        # Campos que el usuario puede editar
        fields = ['foto', 'nombres', 'apellidos', 'cedula', 'nacionalidad', 'perfil_profesional', 'direccion_domiciliaria']
        
        # Diseño para que combine con tus estilos
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'perfil_profesional': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'direccion_domiciliaria': forms.TextInput(attrs={'class': 'form-control'}),
        }