from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    archivo = models.FileField(upload_to='tareas/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
foto = models.ImageField(upload_to='perfil/', null=True, blank=True)

class DatosPersonales(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    nombres = models.CharField(max_length=60)
    apellidos = models.CharField(max_length=60)
    cedula = models.CharField(max_length=10, unique=True)
    nacionalidad = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion_domiciliaria = models.CharField(max_length=100)
    perfil_profesional = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class ExperienciaLaboral(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='experiencias')
    nombre_empresa = models.CharField(max_length=100)
    cargo_desempenado = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

class Curso(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='cursos')
    nombre_curso = models.CharField(max_length=100)
    institucion = models.CharField(max_length=100)
    horas = models.IntegerField()

class ProductoLaboral(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='productos_lab')
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)

class ProductoAcademico(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='productos_acad')
    nombre_recurso = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)

class Recomendacion(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='recomendaciones')
    nombre_persona = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)