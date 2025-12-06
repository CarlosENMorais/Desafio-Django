from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Cadastros
    path('registrar/<str:tipo>/', views.registrar, name='registrar'),
    path('registrar/<str:tipo>/<int:id>/', views.registrar, name='editar_registro'),


    # Relatórios (você precisará criar essas views)
    path('relatorio/alunos/', views.relatorio_alunos, name='relatorio_alunos'),
    path('relatorio/cursos/', views.relatorio_cursos, name='relatorio_cursos'),
    path('relatorio/matriculas/', views.relatorio_matriculas, name='relatorio_matriculas'),
    
    # Outras páginas
    path('historico/<int:id>/', views.historico, name='historico'),


]