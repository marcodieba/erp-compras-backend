# apps/core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Setor(models.Model):
    nome = models.CharField(max_length=100) # Ex: Produção, Lavagem, Caleiro, Manutenção
    codigo = models.CharField(max_length=20, unique=True)
    
class CentroCusto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descricao = models.CharField(max_length=100)
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT)

class User(AbstractUser):
    PERFIS = [
        ('ALMOXARIFE', 'Almoxarife'),
        ('COMPRADOR', 'Comprador'),
        ('GERENTE', 'Gerente Geral'),
        ('ADMIN', 'Administrador do Sistema')
    ]
    perfil = models.CharField(max_length=20, choices=PERFIS)
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True)
    telefone = models.CharField(max_length=20, blank=True)


class TenantModel(models.Model):
    # Futuramente, apontará para uma tabela "Empresa". 
    # Por enquanto, fica anulável para não quebrar a aplicação atual.
    empresa_id = models.IntegerField(null=True, blank=True) 

    class Meta:
        abstract = True