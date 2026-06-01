# apps/compras/services.py
from django.utils import timezone
from datetime import timedelta
from .models import PedidoCompra
from apps.notificacoes.services import NotificacaoService

class PedidoService:
    @staticmethod
    def calcular_sla(prioridade):
        horas = {'EMERGENCIAL': 2, 'ALTA': 8, 'NORMAL': 24}.get(prioridade, 24)
        return timezone.now() + timedelta(hours=horas)

    @staticmethod
    def criar_pedido(dados_pedido, solicitante):
        pedido = PedidoCompra.objects.create(
            **dados_pedido,
            solicitante=solicitante,
            sla_vencimento=PedidoService.calcular_sla(dados_pedido['prioridade'])
        )
        NotificacaoService.notificar_compradores(f"Novo pedido {pedido.numero} criado.")
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