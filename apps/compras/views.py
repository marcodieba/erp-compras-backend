# apps/compras/views.py
import csv
import openpyxl
from reportlab.pdfgen import canvas
from django.utils import timezone

from django.http import HttpResponse

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import PedidoSerializer, CotacaoSerializer, AprovacaoSerializer
from .services import PedidoService
from .models import PedidoCompra, Cotacao, Aprovacao

from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsGerente, IsComprador

from .serializers import AnexoSerializer, ItemPedidoSerializer
from .models import Anexo, ItemPedido

from django.db.models import Count, Sum



class PedidoViewSet(viewsets.ModelViewSet):
    queryset = PedidoCompra.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated] 
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'prioridade', 'setor']
    search_fields = ['numero', 'justificativa', 'observacoes']
    ordering_fields = ['data_criacao', 'sla_vencimento', 'prioridade']

    # A CORREÇÃO ESTÁ AQUI NESTA FUNÇÃO:
    def perform_create(self, serializer):
        # 1. Deixamos o Serializer trabalhar! Ele vai usar aquela função create() 
        # que fizemos no passo anterior para guardar o pedido e os itens.
        pedido = serializer.save(solicitante=self.request.user)
        
        # 2. Se o seu PedidoService tem lógica de enviar emails ou calcular SLA,
        # você deve chamá-lo APÓS o pedido já estar guardado na base de dados:
        # (Comentei a linha abaixo para não dar erro caso o service precise de ajustes)
        # PedidoService.processar_novo_pedido(pedido)

    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        try:
            cotacao_id = request.data.get('cotacao_vencedora_id')
            pedido = PedidoService.aprovar_pedido(pk, request.user, cotacao_id)
            return Response({'status': 'Pedido aprovado com sucesso', 'status_atual': pedido.status})
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class CotacaoViewSet(viewsets.ModelViewSet):
    queryset = Cotacao.objects.all()
    serializer_class = CotacaoSerializer
    permission_classes = [IsComprador]

    def perform_create(self, serializer):
        # Valida se o pedido já está fechado antes de aceitar nova cotação
        pedido = serializer.validated_data['pedido']
        if pedido.status not in ['CRIADO', 'COTACAO', 'REVISAO']:
            raise ValidationError("Não é possível adicionar cotações a este pedido.")
        
        pedido.status = 'COTACAO'
        pedido.save()
        serializer.save()

class AprovacaoViewSet(viewsets.GenericViewSet):
    permission_classes = [IsGerente]

    @action(detail=True, methods=['post'])
    def aprovar_gerente(self, request, pk=None):
        pedido = PedidoCompra.objects.get(pk=pk)
        cotacao_id = request.data.get('cotacao_id')
        
        if pedido.cotacoes.count() < 3:
            return Response(
                {"erro": "Política de compliance falhou: Mínimo de 3 cotações exigido."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        Aprovacao.objects.create(
            pedido=pedido, 
            usuario=request.user, 
            status='APROVADO', 
            comentario=request.data.get('comentario', '')
        )
        
        # Lógica de Service para atualizar status do pedido e notificar
        PedidoService.processar_aprovacao(pedido, cotacao_id)
        
        return Response({"status": "Aprovado com sucesso e encaminhado para compra."})
    
    @action(detail=True, methods=['post'])
    def aprovar_parcialmente(self, request, pk=None):
        pedido = PedidoCompra.objects.get(pk=pk)
        itens_aprovados = request.data.get('itens_aprovados', []) # Lista de IDs
        
        if not itens_aprovados:
            return Response({"erro": "Informe os itens aprovados."}, status=400)
            
        # Lógica: Cancela os itens não aprovados e avança o pedido
        pedido.itens.exclude(id__in=itens_aprovados).delete()
        pedido.status = 'COMPRADO'
        pedido.save()
        
        Aprovacao.objects.create(
            pedido=pedido, usuario=request.user, status='APROVADO_PARCIAL',
            comentario=f"Aprovado parcialmente. Itens excluídos."
        )
        return Response({"status": "Pedido aprovado parcialmente."})

    @action(detail=True, methods=['post'])
    def solicitar_revisao(self, request, pk=None):
        # Retorna o pedido para o comprador buscar novos preços
        pedido = PedidoCompra.objects.get(pk=pk)
        pedido.status = 'REVISAO'
        pedido.save()
        return Response({"status": "Pedido retornado ao comprador para revisão."})


class RelatorioViewSet(viewsets.ViewSet):
    permission_classes = [IsGerente]

    @action(detail=False, methods=['get'])
    def compras_excel(self, request):
        """Gera o relatório de Compras e Custos em Excel"""
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="relatorio_compras_{timezone.now().date()}.xlsx"'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Relatório de Custos"
        
        # Cabeçalhos
        ws.append(['Número Pedido', 'Setor', 'Centro de Custo', 'Status', 'Valor Total (R$)'])
        
        # Dados
        cotacoes_vencedoras = Cotacao.objects.filter(vencedora=True).select_related('pedido__setor', 'pedido__centro_custo')
        for cotacao in cotacoes_vencedoras:
            ws.append([
                cotacao.pedido.numero,
                cotacao.pedido.setor.nome,
                cotacao.pedido.centro_custo.descricao,
                cotacao.pedido.status,
                float(cotacao.valor_total)
            ])
            
        wb.save(response)
        return response

    @action(detail=False, methods=['get'])
    def sla_pdf(self, request):
        """Gera o relatório de SLAs em PDF"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="relatorio_sla_{timezone.now().date()}.pdf"'
        
        p = canvas.Canvas(response)
        p.drawString(100, 800, "Relatório de Auditoria de SLA - Compras Industriais")
        
        y = 750
        atrasados = PedidoCompra.objects.filter(sla_vencimento__lt=timezone.now()).exclude(status='ENTREGUE')
        
        for pedido in atrasados:
            p.drawString(100, y, f"Pedido: {pedido.numero} | Status: {pedido.status} | Venceu em: {pedido.sla_vencimento.strftime('%d/%m/%Y %H:%M')}")
            y -= 20
            if y < 50: # Nova página
                p.showPage()
                y = 800
                
        p.showPage()
        p.save()
        return response


class AnexoViewSet(viewsets.ModelViewSet):
    queryset = Anexo.objects.all()
    serializer_class = AnexoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(enviado_por=self.request.user)



class ItemPedidoViewSet(viewsets.ModelViewSet):
    """
    Endpoint para gerir Itens separadamente (CRUD completo).
    """
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pedido', 'codigo_erp', 'maquina_aplicacao']

class DashboardViewSet(viewsets.ViewSet):
    """
    Endpoint para o Dashboard do Administrador e Gerente Geral.
    """
    permission_classes = [IsGerente]

    @action(detail=False, methods=['get'])
    def metricas(self, request):
        pedidos_pendentes = PedidoCompra.objects.filter(status__in=['CRIADO', 'COTACAO', 'APROVACAO']).count()
        pedidos_entregues = PedidoCompra.objects.filter(status='ENTREGUE').count()
        pedidos_atrasados = PedidoCompra.objects.filter(
            sla_vencimento__lt=timezone.now(),
            status__in=['CRIADO', 'COTACAO', 'APROVACAO']
        ).count()
        
        # Custos totais agregados por compras já entregues
        total_gasto = Cotacao.objects.filter(
            vencedora=True, 
            pedido__status='ENTREGUE'
        ).aggregate(total=Sum('valor_total'))['total'] or 0.00

        return Response({
            'pedidos_pendentes': pedidos_pendentes,
            'pedidos_entregues': pedidos_entregues,
            'pedidos_com_sla_vencido': pedidos_atrasados,
            'total_gasto_entregue': total_gasto,
        })