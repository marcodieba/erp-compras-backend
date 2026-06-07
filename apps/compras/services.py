# apps/compras/services.py
from django.utils import timezone
from datetime import timedelta
from .models import PedidoCompra
from apps.notificacoes.services import NotificacaoService

class PedidoService:
    @staticmethod
    def calcular_sla(prioridade):
        # Mapeamento do tempo de SLA baseado na prioridade do Django (em maiúsculas)
        horas = {
            'URGENTE': 2, 
            'ALTA': 8, 
            'MEDIA': 24, 
            'BAIXA': 48
        }.get(prioridade, 24) # Padrão é 24h
        
        return timezone.now() + timedelta(hours=horas)

    @staticmethod
    def processar_novo_pedido(pedido):
        """
        Executa as regras de negócio APÓS o pedido e os itens serem salvos no banco.
        """
        # 1. Calcula e define a data limite do SLA
        pedido.sla_vencimento = PedidoService.calcular_sla(pedido.prioridade)
        
        # Salvamos apenas o campo de SLA para não sobreescrever nada acidentalmente
        pedido.save(update_fields=['sla_vencimento']) 

        # 2. Dispara a notificação para os compradores
        NotificacaoService.notificar_compradores(f"Novo pedido #{pedido.numero} ({pedido.titulo}) aguardando cotação.")
        
        return pedido

    @staticmethod
    def aprovar_pedido(pedido_id, gerente, cotacao_vencedora_id):
        pedido = PedidoCompra.objects.get(id=pedido_id)
        # Regra: Mínimo 3 cotações
        if pedido.cotacoes.count() < 3:
            raise ValueError("O pedido precisa de no mínimo 3 cotações para aprovação.")
        
        pedido.status = 'COMPRADO'
        pedido.save()
        
        cotacao = pedido.cotacoes.get(id=cotacao_vencedora_id)
        cotacao.vencedora = True
        cotacao.save()
        
        # Gera evento para auditoria/rastreio e notifica comprador
        NotificacaoService.notificar_usuario(pedido.comprador, f"Pedido {pedido.numero} aprovado. Iniciar trâmites de compra.")
        return pedido