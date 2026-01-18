from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from django.forms import inlineformset_factory, widgets
from django.http import HttpResponse
from io import BytesIO

# --- ÚNICA IMPORTACIÓN PARA EL PDF (REPORTLAB) ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER

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
    perfil, created = DatosPersonales.objects.get_or_create(user=request.user)
    
    ExperienciaFormSet = inlineformset_factory(
        DatosPersonales, ExperienciaLaboral, 
        fields=['nombre_empresa', 'cargo_desempenado', 'fecha_inicio', 'fecha_fin'], 
        widgets={
            'fecha_inicio': widgets.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'fecha_fin': widgets.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
        },
        extra=1, can_delete=True
    )
    
    CursoFormSet = inlineformset_factory(DatosPersonales, Curso, fields=['nombre_curso', 'institucion', 'horas'], extra=1, can_delete=True)
    ProdLabFormSet = inlineformset_factory(DatosPersonales, ProductoLaboral, fields=['nombre_producto', 'descripcion'], extra=1, can_delete=True)
    ProdAcadFormSet = inlineformset_factory(DatosPersonales, ProductoAcademico, fields=['nombre_recurso', 'descripcion'], extra=1, can_delete=True)

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        formset_exp = ExperienciaFormSet(request.POST, instance=perfil)
        formset_cur = CursoFormSet(request.POST, instance=perfil)
        formset_lab = ProdLabFormSet(request.POST, instance=perfil)
        formset_acad = ProdAcadFormSet(request.POST, instance=perfil)
        
        is_valid = all([form.is_valid(), formset_exp.is_valid(), formset_cur.is_valid(), formset_lab.is_valid(), formset_acad.is_valid()])

        if is_valid:
            perfil_obj = form.save()
            formset_exp.instance = perfil_obj
            formset_exp.save()
            formset_cur.instance = perfil_obj
            formset_cur.save()
            formset_lab.instance = perfil_obj
            formset_lab.save()
            formset_acad.instance = perfil_obj
            formset_acad.save()
            return redirect('hoja_vida')
    else:
        form = PerfilForm(instance=perfil)
        formset_exp = ExperienciaFormSet(instance=perfil)
        formset_cur = CursoFormSet(instance=perfil)
        formset_lab = ProdLabFormSet(instance=perfil)
        formset_acad = ProdAcadFormSet(instance=perfil)

    return render(request, 'editar_perfil.html', {
        'form': form, 'formset_exp': formset_exp, 'formset_cur': formset_cur,
        'formset_lab': formset_lab, 'formset_acad': formset_acad
    })

# --- FUNCIÓN DE DESCARGA PDF RECONSTRUIDA PARA REPORTLAB ---
@login_required
def descargar_cv_pdf(request):
    # 1. Traemos los datos (usando los nombres de campos correctos)
    perfil = DatosPersonales.objects.filter(user=request.user).first()
    # CAMBIO AQUÍ: Usamos 'perfil' en lugar de 'datos_personales'
    experiencias = ExperienciaLaboral.objects.filter(perfil=perfil)
    cursos = Curso.objects.filter(perfil=perfil)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=LETTER)
    
    # --- Dibujando el CV ---
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, 750, "HOJA DE VIDA")
    
    p.setFont("Helvetica-Bold", 14)
    nombre = f"{perfil.nombres} {perfil.apellidos}" if perfil else request.user.username
    p.drawString(100, 725, nombre.upper())
    p.line(100, 720, 500, 720)
    
    p.setFont("Helvetica", 11)
    y = 690
    if perfil:
        p.drawString(100, y, f"Email: {request.user.email}")
        y -= 20
        p.drawString(100, y, f"Teléfono: {perfil.telefono}")
        y -= 20
        p.drawString(100, y, f"Ubicación: {perfil.direccion}")
        y -= 40

    # Experiencia Laboral
    p.setFont("Helvetica-Bold", 13)
    p.drawString(100, y, "EXPERIENCIA LABORAL")
    y -= 20
    
    p.setFont("Helvetica", 11)
    for exp in experiencias:
        p.drawString(100, y, f"• {exp.cargo_desempenado} en {exp.nombre_empresa}")
        y -= 15
        p.setFont("Helvetica-Oblique", 9)
        p.drawString(115, y, f"({exp.fecha_inicio} a {exp.fecha_fin})")
        y -= 25
        if y < 100:
            p.showPage()
            y = 750

    # Cursos
    y -= 10
    p.setFont("Helvetica-Bold", 13)
    p.drawString(100, y, "CURSOS Y FORMACIÓN")
    y -= 20
    for c in cursos:
        p.drawString(100, y, f"• {c.nombre_curso} ({c.institucion}) - {c.horas}h")
        y -= 20

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', 
                        headers={'Content-Disposition': 'attachment; filename="CV_Alexander_Alarcon.pdf"'})

def helloworld(request):
    return render(request, 'helloworld.html')