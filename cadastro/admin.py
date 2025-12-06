from django.contrib import admin
from .models import Aluno, Curso, Matricula

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cpf', 'data_de_ingresso')
    search_fields = ('nome', 'cpf', 'email')

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'carga_horaria', 'valor_da_inscrissao', 'status')
    list_filter = ('status',)
    search_fields = ('nome', 'carga_horaria', 'valor_da_inscrissao')

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'curso', 'data_matricula', 'pago')
    list_filter = ('pago',)
    search_fields = ('aluno__nome',
                     'aluno__cpf',
                     'aluno__email', 
                     'curso__nome',
                     'curso__carga_horaria',
                     'curso__valor_da_inscrissao',
                     'data_matricula')