from django.db import models
from django.core.exceptions import ValidationError


class Aluno(models.Model):
    nome = models.CharField()
    email = models.EmailField(unique=True)
    cpf = models.CharField(unique=True, max_length=11)
    data_de_ingresso = models.DateField()

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

class Curso(models.Model):
    nome = models.CharField()
    carga_horaria = models.IntegerField()
    valor_da_inscrissao = models.DecimalField(max_digits=10, max_length=10, decimal_places=2)
    status = models.BooleanField(default=True)

    def __str__(self):
        status = "Ativo" if self.status else "Inativo"
        return f"{self.nome} ({status})"
    
class Matricula(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.PROTECT, related_name='matriculas')
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name='matriculas')
    data_matricula = models.DateField()
    pago = models.BooleanField(default=False)

    class Meta:
        unique_together = ('aluno', 'curso')
    
    def clean(self):
        if not self.curso.status:
            raise ValidationError("Não é possível matricular aluno em curso inativo")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Pago" if self.pago else "Pendente"
        return f"{self.aluno.nome} - {self.curso.nome} ({status})"