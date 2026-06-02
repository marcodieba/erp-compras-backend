# apps/compras/models.py
import uuid
from django.db import models
from apps.core.models import User, Setor, CentroCusto
from simple_history.models import HistoricalRecords
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class PedidoCompra(models.Model):
    STATUS_CHOICES = [
        ('CRIADO', 'Criado pelo Almoxarife'),
        ('COTACAO', 'Em Cotação'),
        ('APROVACAO', 'Aguardando Aprovação'),
        ('REVISAO', 'Revisão Solicitada'),
        ('COMPRADO', 'Compra Efetuada'),
        ('TRANSITO', 'Em Transporte'),
        ('ENTREGUE', 'Entregue')
    ]
    
    # Atualizado para bater exatamente com as opções do Frontend
    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveIntegerField(unique=True, editable=False)
    titulo = models.CharField(max_length=200) # NOVO: Para listagens rápidas
    solicitante = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pedidos_solicitados')
    comprador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pedidos_comprados')
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.PROTECT)
    prioridade = models.CharField(max_length=15, choices=PRIORIDADE_CHOICES, default='MEDIA')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='CRIADO')
    justificativa = models.TextField()
    observacoes = models.TextField(blank=True, null=True) # NOVO: Notas extras do pedido
    data_criacao = models.DateTimeField(auto_now_add=True)
    sla_vencimento = models.DateTimeField(null=True, blank=True)
    
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo_pedido = PedidoCompra.objects.order_by('-numero').first()
            if ultimo_pedido:
                self.numero = ultimo_pedido.numero + 1
            else:
                self.numero = 1
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-data_criacao']

class ItemPedido(models.Model):
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='itens')
    codigo_erp = models.CharField(max_length=50, blank=True)
    descricao = models.CharField(max_length=255)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    unidade = models.CharField(max_length=10)
    maquina_aplicacao = models.CharField(max_length=100, blank=True)
    observacao = models.CharField(max_length=255, blank=True, null=True) # NOVO: Para bater com o form de itens
    prazo_desejado = models.DateField()

class Cotacao(models.Model):
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='cotacoes')
    fornecedor = models.ForeignKey('logistica.Fornecedor', on_delete=models.PROTECT)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    frete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prazo_entrega_dias = models.PositiveIntegerField()
    condicao_pagamento = models.CharField(max_length=100)
    vencedora = models.BooleanField(default=False)


class Anexo(models.Model):
    TIPO_ARQUIVO = [('PDF', 'Documento PDF'), ('IMG', 'Imagem'), ('XLS', 'Planilha')]
    
    arquivo = models.FileField(upload_to='anexos/%Y/%m/')
    tipo = models.CharField(max_length=3, choices=TIPO_ARQUIVO)
    enviado_por = models.ForeignKey('core.User', on_delete=models.PROTECT)
    data_envio = models.DateTimeField(auto_now_add=True)
    
    # Generic Relations para atrelar a Pedido, Item ou Cotação
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Aprovacao(models.Model):
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='aprovacoes')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=[('APROVADO', 'Aprovado'), ('REJEITADO', 'Rejeitado')])
    comentario = models.TextField(blank=True)
    data = models.DateTimeField(auto_now_add=True)
    
    history = HistoricalRecords()