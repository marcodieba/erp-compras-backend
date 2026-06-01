# apps/compras/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import PedidoCompra
from apps.notificacoes.services import NotificacaoService

@shared_task
def verificar_slas_vencidos():
    agora = timezone.now()
    pedidos_atrasados = PedidoCompra.objects.filter(
        sla_vencimento__lt=agora,
        status__in=['CRIADO', 'COTACAO', 'APROVACAO']
    )
    
    for pedido in pedidos_atrasados:
        NotificacaoService.alerta_sla_vencido(pedido)

@shared_task
def verificar_atualizacao_rastreamento():
    # Verifica se os compradores atualizaram o andamento 2x ao dia
    # Lógica de verificação de timestamp de rastreamento
    pass