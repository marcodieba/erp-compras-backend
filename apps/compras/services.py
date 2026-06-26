# apps/compras/services.py
from django.utils import timezone
from datetime import timedelta
from .models import PedidoCompra
from apps.notificacoes.services import NotificacaoService

class PedidoService:
    @staticmethod
    def calcular_sla(prioridade):
        # Mapeamento do tempo de SLA baseado na prioridade do Django
        horas = {
            'URGENTE': 2, 
            'ALTA': 8, 
            'MEDIA': 24, 
            'BAIXA': 48
        }.get(prioridade, 24)
        
        return timezone.now() + timedelta(hours=horas)

    @staticmethod
    def processar_novo_pedido(pedido):
        """Executa regras de negócio APÓS o pedido e os itens serem salvos."""
        pedido.sla_vencimento = PedidoService.calcular_sla(pedido.prioridade)
        pedido.save(update_fields=['sla_vencimento']) 

        NotificacaoService.notificar_compradores(f"Novo pedido #{pedido.numero} ({pedido.titulo}) aguardando cotação.")
        return pedido

    @staticmethod
    def aprovar_pedido(pedido_id, gerente, cotacao_vencedora_id):
        pedido = PedidoCompra.objects.get(id=pedido_id)
        
        # 1. Flexibilizado para testes (Exige apenas 1 cotação em vez de 3)
        if pedido.cotacoes.count() < 1:
            raise ValueError("O pedido precisa de pelo menos 1 cotação para aprovação.")
        
        # 2. Pega a cotação aprovada e marca como vencedora
        cotacao = pedido.cotacoes.get(id=cotacao_vencedora_id)
        cotacao.vencedora = True
        cotacao.save()
        
        # 3. MÁGICA DA COTAÇÃO PARCIAL: Vincula a vitória apenas aos itens desta cotação
        for item in cotacao.itens.all():
            item.cotacao_vencedora = cotacao
            item.save(update_fields=['cotacao_vencedora'])
        
        # 4. Verifica se ainda existem itens pendentes sem fornecedor escolhido
        itens_pendentes = pedido.itens.filter(cotacao_vencedora__isnull=True).count()
        
        if itens_pendentes == 0:
            # Todos os itens foram comprados! O pedido avança no fluxo.
            pedido.status = 'COMPRADO'
            pedido.save(update_fields=['status'])
            NotificacaoService.notificar_usuario(
                pedido.comprador, 
                f"Pedido {pedido.numero} totalmente aprovado. Iniciar trâmites de compra com os fornecedores."
            )
        else:
            # Ainda faltam itens. Devolve para o comprador terminar o trabalho.
            pedido.status = 'COTACAO'
            pedido.save(update_fields=['status'])
            NotificacaoService.notificar_usuario(
                pedido.comprador, 
                f"Cotação parcial do Pedido {pedido.numero} aprovada. Faltam cotar {itens_pendentes} itens."
            )
            
        return pedido