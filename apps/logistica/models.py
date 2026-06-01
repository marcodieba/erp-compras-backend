# apps/logistica/models.py
from django.db import models
from apps.compras.models import PedidoCompra
from simple_history.models import HistoricalRecords

class Fornecedor(models.Model):
    razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    contato_nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    nota_avaliacao = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    historico_atrasos = models.PositiveIntegerField(default=0) # Incrementado via Celery se SLA de entrega falhar
    
    history = HistoricalRecords()

class Rastreamento(models.Model):
    ESTAGIOS = [
        ('COMPRA_EFETUADA', 'Compra Efetuada'),
        ('NF_EMITIDA', 'NF Emitida'),
        ('SEPARACAO', 'Em Separação'),
        ('COLETADO', 'Coletado / Embarcado'), # Importante se utilizar frota própria para buscar insumos
        ('TRANSPORTE', 'Em Transporte'),
        ('ENTREGUE', 'Entregue')
    ]
    pedido = models.OneToOneField(PedidoCompra, on_delete=models.CASCADE, related_name='rastreamento')
    estagio_atual = models.CharField(max_length=20, choices=ESTAGIOS, default='COMPRA_EFETUADA')
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    previsao_entrega = models.DateField()
    observacoes = models.TextField(blank=True)
    
    history = HistoricalRecords()