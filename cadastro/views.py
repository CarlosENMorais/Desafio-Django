from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.db.models import Sum, Q, Count, DecimalField, Case, When
from django.db.models.functions import Coalesce
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Aluno, Curso, Matricula
from datetime import date
from django import forms

## HOME 
def home(request):
    with connection.cursor() as cursor:

        # Total de alunos cadastrados
        cursor.execute("SELECT COUNT(*) FROM cadastro_aluno;")
        total_alunos = cursor.fetchone()[0]

        # Total de cursos ativos (status = TRUE)
        cursor.execute("SELECT COUNT(*) FROM cadastro_curso WHERE status = TRUE;")
        cursos_ativos = cursor.fetchone()[0]

        # Matrículas pagas e pendentes
        cursor.execute("SELECT COUNT(*) FROM cadastro_matricula WHERE pago = TRUE;")
        matriculas_pagas = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM cadastro_matricula WHERE pago = FALSE;")
        matriculas_pendentes = cursor.fetchone()[0]

        # Soma dos valores pagos e não pagos
        cursor.execute("""
            SELECT COALESCE(SUM(c.valor_da_inscrissao), 0)
            FROM cadastro_matricula m
            JOIN cadastro_curso c ON c.id = m.curso_id
            WHERE m.pago = TRUE;
        """)
        valor_pago = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(c.valor_da_inscrissao), 0)
            FROM cadastro_matricula m
            JOIN cadastro_curso c ON c.id = m.curso_id
            WHERE m.pago = FALSE;
        """)
        valor_pendente = cursor.fetchone()[0]
    
    context = {
        "total_alunos": total_alunos,
        "cursos_ativos": cursos_ativos,
        "matriculas_pagas": matriculas_pagas,
        "matriculas_pendentes": matriculas_pendentes,
        "valor_pago": valor_pago,
        "valor_pendente": valor_pendente,
    }
    
    return render(request, 'homepage.html', context)

## REGISTRO

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = '__all__'

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = '__all__'

class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = "__all__"
        widgets = {
            "data_matricula": forms.DateInput(attrs={
                "type": "date", 
                "class": "form-control"
            })
        }

def registrar(request, tipo, id=None):
    forms_map = {
        'alunos': (AlunoForm, 'Cadastrar Aluno'),
        'cursos': (CursoForm, 'Cadastrar Curso'),
        'matriculas': (MatriculaForm, 'Realizar Matrícula')
    }

    FormClass, titulo_base = forms_map[tipo]

    # Se for edição, busca o registro
    instance = None
    if id:
        if tipo == 'alunos':
            instance = Aluno.objects.get(id=id)
        elif tipo == 'cursos':
            instance = Curso.objects.get(id=id)
        elif tipo == 'matriculas':
            instance = Matricula.objects.get(id=id)
        titulo = f"Editar {tipo[:-1].capitalize()}"
    else:
        titulo = titulo_base

    # Lidar com deleção
    if request.method == 'POST' and 'deletar' in request.POST:
        if instance:
            instance.delete()
            messages.success(request, f'{tipo[:-1].capitalize()} deletado com sucesso!')
            return redirect('home')

    # Formulário preenchido para edição
    if request.method == 'POST':
        form = FormClass(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f'{titulo} realizado com sucesso!')
            return redirect('home')
    else:
        form = FormClass(instance=instance)

    return render(request, 'registro.html', {
        'form': form,
        'titulo': titulo,
        'tipo': tipo,
        'editando': id is not None  # Passa se está editando
    })

## RELATÓRIOS

def relatorio_alunos(request):
    alunos = Aluno.objects.all()

    dados = []
    for aluno in alunos:
        matriculas = aluno.matriculas.all()

        ativas = matriculas.filter(curso__status=True)
        inativas = matriculas.filter(curso__status=False)

        dados.append({
            "id": aluno.id,
            "nome": aluno.nome,
            "matriculas_ativas": ativas.count(),
            "matriculas_ativas_pagas": ativas.filter(pago=True).count(),
            "matriculas_ativas_pendentes": ativas.filter(pago=False).count(),
            "matriculas_inativas": inativas.count(),
        })

    return render(request, "relatorio_alunos.html", {"dados": dados})

def relatorio_cursos(request):
    # filtros GET
    nome_curso = request.GET.get('nome', '')
    status = request.GET.get('status', '')

    cursos = Curso.objects.all()

    if nome_curso:
        cursos = cursos.filter(nome__icontains=nome_curso)

    if status in ['ativo', 'inativo']:
        cursos = cursos.filter(status=True) if status == 'ativo' else cursos.filter(status=False)

    # Annotate com dados agregados por curso
    cursos = cursos.annotate(
        total_matriculados=Count('matriculas'),
        total_pago=Sum(
            Case(When(matriculas__pago=True, then='valor_da_inscrissao'), 
                 default=0, output_field=DecimalField())
        ),
        total_pendente=Sum(
            Case(When(matriculas__pago=False, then='valor_da_inscrissao'), 
                 default=0, output_field=DecimalField())
        )
    )

    context = {
        'cursos': cursos,
        'nome_curso': nome_curso,
        'status': status,
    }
    return render(request, 'relatorio_cursos.html', context)

def relatorio_matriculas(request):
    matriculas = Matricula.objects.select_related("aluno", "curso")

    # ---------------- FILTRO POR PERÍODO ----------------
    data_inicio = request.GET.get("inicio")
    data_fim = request.GET.get("fim")

    if data_inicio:
        matriculas = matriculas.filter(data_matricula__gte=data_inicio)
    if data_fim:
        matriculas = matriculas.filter(data_matricula__lte=data_fim)

    # ---------------- BARRA DE PESQUISA ----------------
    pesquisa = request.GET.get("q")
    if pesquisa:
        matriculas = matriculas.filter(
            Q(aluno__nome__icontains=pesquisa) |
            Q(curso__nome__icontains=pesquisa)
        )

    # ---------------- CÁLCULO DE VALORES ----------------
    for m in matriculas:
        m.valor_pago = m.curso.valor_da_inscrissao if m.pago else 0
        m.valor_pendente = 0 if m.pago else m.curso.valor_da_inscrissao

    total_pago = sum(m.valor_pago for m in matriculas)
    total_pendente = sum(m.valor_pendente for m in matriculas)

    context = {
        "matriculas": matriculas,
        "total_pago": total_pago,
        "total_pendente": total_pendente,
    }
    return render(request, "relatorio_matriculas.html", context)

## OUTROS
def historico(request, id):
    aluno = get_object_or_404(Aluno, id=id)

    matriculas = Matricula.objects.filter(aluno=aluno).select_related('curso').order_by(
        '-curso__status',            # cursos ativos primeiro
        'data_matricula'             # depois ordena pela data
    )

    # Cálculo das horas
    total_horas = sum(m.curso.carga_horaria for m in matriculas)
    horas_ativas = sum(m.curso.carga_horaria for m in matriculas if m.curso.status)
    horas_inativas = total_horas - horas_ativas

    contexto = {
        'aluno': aluno,
        'matriculas': matriculas,
        'total_horas': total_horas,
        'horas_ativas': horas_ativas,
        'horas_inativas': horas_inativas,
    }

    return render(request, 'historico.html', contexto)



