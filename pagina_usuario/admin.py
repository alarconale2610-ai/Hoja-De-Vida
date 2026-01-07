from django.contrib import admin
from .models import (
    DatosPersonales, ExperienciaLaboral, Curso, 
    ProductoLaboral, ProductoAcademico, Recomendacion
)

# ==========================================================
# 1. CONFIGURACIÓN GLOBAL DEL PANEL DE ADMINISTRACIÓN
# ==========================================================
# Esto cambia el título del panel y el botón "Ver el sitio"
admin.site.site_header = "Panel de Control TASKFLOW"
admin.site.site_title = "Admin TaskFlow"
admin.site.index_title = "Bienvenido al Administrador"
admin.site.site_url = '/'  # Apunta al inicio de tu web (localhost:8000/)

# ==========================================================
# 2. CONFIGURACIÓN DE INLINES
# ==========================================================
class ExperienciaInline(admin.TabularInline):
    model = ExperienciaLaboral
    extra = 1

class CursoInline(admin.TabularInline):
    model = Curso
    extra = 1

class RecomendacionInline(admin.TabularInline):
    model = Recomendacion
    extra = 1

class ProductoLaboralInline(admin.TabularInline):
    model = ProductoLaboral
    extra = 1

class ProductoAcademicoInline(admin.TabularInline):
    model = ProductoAcademico
    extra = 1

# ==========================================================
# 3. REGISTRO DE MODELOS Y PERSONALIZACIÓN
# ==========================================================

@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'cedula', 'nacionalidad')
    search_fields = ('nombres', 'apellidos', 'cedula')
    # Inlines permiten editar todo desde la misma ficha del usuario
    inlines = [
        ExperienciaInline, 
        CursoInline, 
        RecomendacionInline, 
        ProductoLaboralInline, 
        ProductoAcademicoInline
    ]

# Registramos los modelos individuales para permitir edición por separado
admin.site.register(ExperienciaLaboral)
admin.site.register(Curso)
admin.site.register(ProductoLaboral)
admin.site.register(ProductoAcademico)
admin.site.register(Recomendacion)