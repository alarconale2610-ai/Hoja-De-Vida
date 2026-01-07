from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone

# 1. IMPORTA SOLO LOS MODELOS AQUÍ
from .models import Task, DatosPersonales, ExperienciaLaboral, Curso, ProductoLaboral, ProductoAcademico, Recomendacion

from .form import PerfilForm

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        # Mejora: Usamos el formulario de Django para validar seguridad de contraseñas
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signup.html', {'form': form, 'error': 'Datos inválidos o contraseñas débiles'})

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm()})
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signin.html', {'form': form, 'error': 'Usuario o contraseña incorrectos'})

@login_required
def signout(request):
    logout(request)
    return redirect('home')

@login_required
def tasks(request):
    # Mejora: Ordenamos por las más recientes primero
    tasks_pending = Task.objects.filter(user=request.user, datecompleted__isnull=True).order_by('-created')
    tasks_completed = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'task.html', {'tasks_pending': tasks_pending, 'tasks_completed': tasks_completed})

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_tasks.html')
    else:
        # Agregamos validación básica para que no se cree una tarea vacía
        title = request.POST.get('title')
        if title:
            Task.objects.create(
                title=title,
                description=request.POST.get('description', ''),
                important='important' in request.POST,
                archivo=request.FILES.get('archivo'),
                user=request.user
            )
            return redirect('tasks')
        return render(request, 'create_tasks.html', {'error': 'El título es obligatorio'})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.datecompleted = timezone.now()
    task.save()
    return redirect('tasks')

@login_required
def hoja_vida(request):
    # Usamos select_related o prefetch_related para que la página cargue más rápido
    datos = DatosPersonales.objects.filter(user=request.user).first()
    return render(request, 'hoja de vida.html', {'perfil': datos})

@login_required
def editar_perfil(request):
    perfil, created = DatosPersonales.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('hoja_vida')
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'editar_perfil.html', {'form': form})


def helloworld(request):
    return render(request, 'helloworld.html')

