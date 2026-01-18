from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.signout, name='logout'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('hojavida/', views.hoja_vida, name='hoja_vida'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('descargar-cv/', views.descargar_cv_pdf, name='descargar_cv'),
]