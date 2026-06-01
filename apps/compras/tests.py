# apps/compras/tests.py
from django.test import TestCase
from django.utils import timezone
from apps.core.models import User, Setor, CentroCusto
from apps.compras.models import PedidoCompra
from apps.compras.services import PedidoService

class PedidoCompraTests(TestCase):
    def setUp(self):
        # Preparar dados de teste
        self.setor = Setor.objects.create(nome="Curtume - Lavagem", codigo="LAV-01")
        self.centro_custo = CentroCusto.objects.create(codigo="CC-001", descricao="Insumos Químicos", setor=self.setor)
        self.usuario = User.objects.create_user(username="almoxarife", password="123", perfil="ALMOXARIFE", setor=self.setor)

    def test_criacao_pedido_com_sla_emergencial(self):
        """Valida se um pedido emergencial calcula o SLA de 2 horas corretamente."""
        dados_pedido = {
            'setor': self.setor,
            'centro_custo': self.centro_custo,
            'prioridade': 'EMERGENCIAL',
            'justificativa': 'Falta de tensoativos para lavagem, risco de paragem da produção.'
        }
        
        pedido = PedidoService.criar_pedido(dados_pedido, solicitante=self.usuario)
        
        # O SLA tem de ser aproximadamente 2 horas a partir de agora
        diferenca_horas = (pedido.sla_vencimento - timezone.now()).total_seconds() / 3600
        
        self.assertEqual(pedido.status, 'CRIADO')
        self.assertTrue(1.9 < diferenca_horas < 2.1, "O SLA emergencial falhou o cálculo de 2 horas.")