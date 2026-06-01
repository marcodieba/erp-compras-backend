# apps/logistica/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Rastreamento
from apps.notificacoes.services import NotificacaoService

@shared_task
def verificar_atualizacao_rastreamento():
    """
    Roda a cada 4 horas. Verifica se pedidos em trânsito não foram atualizados nas últimas 12h.
    """
    limite_tempo = timezone.now() - timedelta(hours=12)
    
    rastreios_pendentes = Rastreamento.objects.filter(
        pedido__status__in=['COMPRADO', 'TRANSITO'],
        ultima_atualizacao__lt=limite_tempo
    )
    
    for rastreio in rastreios_pendentes:
        comprador = rastreio.pedido.comprador
        NotificacaoService.enviar_alerta(
            usuario=comprador,
            tipo='URGENTE',
            mensagem=f"Obrigatório: Atualize o rastreamento do pedido {rastreio.pedido.numero}. Última atualização há mais de 12h."
        )

@shared_task
def gerar_relatorio_diario_compras():
    """
    Gera um relatório Excel consolidando compras do dia e envia para os Gerentes e Admin.
    """
    # Lógica de geração de Pandas DataFrame -> Excel -> Envio de Email
    pass