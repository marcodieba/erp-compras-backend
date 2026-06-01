# apps/notificacoes/services.py
from .models import Notificacao
from apps.core.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class NotificacaoService:
    @staticmethod
    def _enviar_websocket(usuario_id, mensagem):
        """
        Função interna para disparar a mensagem em tempo real para o frontend
        usando o Django Channels (Redis).
        """
        channel_layer = get_channel_layer()
        if channel_layer:
            # Envia para o grupo de WebSockets específico deste utilizador
            async_to_sync(channel_layer.group_send)(
                f"user_{usuario_id}",
                {
                    "type": "enviar_notificacao", # Tem de bater certo com o método no consumers.py
                    "mensagem": mensagem
                }
            )

    @staticmethod
    def notificar_usuario(usuario, mensagem, tipo='INFO'):
        """Cria a notificação no banco de dados e dispara via WebSocket."""
        # Salva no banco (para histórico e auditoria)
        Notificacao.objects.create(usuario=usuario, mensagem=mensagem, tipo=tipo)
        
        # Dispara em tempo real
        NotificacaoService._enviar_websocket(usuario.id, mensagem)

    @staticmethod
    def notificar_compradores(mensagem):
        """Dispara um aviso para todos os utilizadores com perfil COMPRADOR."""
        compradores = User.objects.filter(perfil='COMPRADOR')
        for comprador in compradores:
            NotificacaoService.notificar_usuario(comprador, mensagem, tipo='INFO')

    @staticmethod
    def alerta_sla_vencido(pedido):
        """Notifica os gerentes e o comprador responsável sobre o atraso de SLA."""
        mensagem = f"ALERTA SLA VENCIDO: Pedido {pedido.numero} (Status: {pedido.status}) ultrapassou o tempo limite."
        
        gerentes = User.objects.filter(perfil='GERENTE')
        for gerente in gerentes:
            NotificacaoService.notificar_usuario(gerente, mensagem, tipo='SLA')
        
        if pedido.comprador:
            NotificacaoService.notificar_usuario(pedido.comprador, mensagem, tipo='SLA')

    @staticmethod
    def enviar_alerta(usuario, tipo, mensagem):
        """Atalho flexível usado pelo módulo de Logística."""
        NotificacaoService.notificar_usuario(usuario, mensagem, tipo=tipo)