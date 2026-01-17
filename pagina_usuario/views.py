from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from django.forms import inlineformset_factory, widgets

# Modelos y Formularios
from .models import Task, DatosPersonales, ExperienciaLaboral, Curso, ProductoLaboral, ProductoAcademico, Recomendacion
from .form import PerfilForm

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signup.html', {'form': form, 'error': 'Datos inválidos'})

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
    tasks_pending = Task.objects.filter(user=request.user, datecompleted__isnull=True).order_by('-created')
    tasks_completed = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'task.html', {'tasks_pending': tasks_pending, 'tasks_completed': tasks_completed})

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_tasks.html')
    else:
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
    datos = DatosPersonales.objects.filter(user=request.user).first()
    return render(request, 'hoja_vida.html', {'perfil': datos})

@login_required
def editar_perfil(request):
    # Obtenemos o creamos el perfil del usuario actual
    perfil, created = DatosPersonales.objects.get_or_create(user=request.user)
    
    # 1. Fábrica de Experiencia Laboral (con widgets de fecha)
    ExperienciaFormSet = inlineformset_factory(
        DatosPersonales, ExperienciaLaboral, 
        fields=['nombre_empresa', 'cargo_desempenado', 'fecha_inicio', 'fecha_fin'], 
        widgets={
            'fecha_inicio': widgets.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'fecha_fin': widgets.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
        },
        extra=1, can_delete=True
    )
    
    # 2. Fábrica de Cursos
    CursoFormSet = inlineformset_factory(
        DatosPersonales, Curso, 
        fields=['nombre_curso', 'institucion', 'horas'], 
        extra=1, can_delete=True
    )

    # 3. NUEVO: Fábrica de Proyectos Laborales
    ProdLabFormSet = inlineformset_factory(
        DatosPersonales, ProductoLaboral, 
        fields=['nombre_producto', 'descripcion'], 
        extra=1, can_delete=True
    )
    
    # 4. NUEVO: Fábrica de Proyectos Académicos
    ProdAcadFormSet = inlineformset_factory(
        DatosPersonales, ProductoAcademico, 
        fields=['nombre_recurso', 'descripcion'], 
        extra=1, can_delete=True
    )

   # AQUÍ ES DONDE AGREGAS EL BLOQUE QUE ME PASASTE
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        formset_exp = ExperienciaFormSet(request.POST, instance=perfil)
        formset_cur = CursoFormSet(request.POST, instance=perfil)
        formset_lab = ProdLabFormSet(request.POST, instance=perfil)
        formset_acad = ProdAcadFormSet(request.POST, instance=perfil)
        
        # Guardamos en una variable si TODO es válido
        is_valid = all([
            form.is_valid(),
            formset_exp.is_valid(),
            formset_cur.is_valid(),
            formset_lab.is_valid(),
            formset_acad.is_valid()
        ])

        if is_valid:
            # Guardamos el perfil principal
            perfil_obj = form.save()
            
            # Guardamos cada formset asegurando la relación con el perfil
            formset_exp.instance = perfil_obj
            formset_exp.save()
            
            formset_cur.instance = perfil_obj
            formset_cur.save()
            
            formset_lab.instance = perfil_obj
            formset_lab.save()
            
            formset_acad.instance = perfil_obj
            formset_acad.save()
            
            return redirect('hoja_vida') # Si todo sale bien, te manda a tu CV
        else:
            # Si algo falla, la terminal te dirá la verdad
            print("--- ERRORES DETECTADOS ---")
            print("Perfil:", form.errors)
            print("Exp:", formset_exp.errors)
            print("Cur:", formset_cur.errors)
            print("Lab:", formset_lab.errors)
            print("Acad:", formset_acad.errors)
    else:
        # Carga inicial para mostrar los datos que ya existen
        form = PerfilForm(instance=perfil)
        formset_exp = ExperienciaFormSet(instance=perfil)
        formset_cur = CursoFormSet(instance=perfil)
        formset_lab = ProdLabFormSet(instance=perfil)
        formset_acad = ProdAcadFormSet(instance=perfil)

    return render(request, 'editar_perfil.html', {
        'form': form,
        'formset_exp': formset_exp,
        'formset_cur': formset_cur,
        'formset_lab': formset_lab,
        'formset_acad': formset_acad
    })


def helloworld(request):
    return render(request, 'helloworld.html')