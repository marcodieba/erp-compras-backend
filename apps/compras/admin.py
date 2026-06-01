from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import PedidoCompra, ItemPedido, Cotacao

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1

@admin.register(PedidoCompra)
class PedidoCompraAdmin(SimpleHistoryAdmin): # Adiciona a aba "Histórico" (Auditoria) automaticamente
    list_display = ('numero', 'solicitante', 'setor', 'prioridade', 'status', 'sla_vencimento')
    list_filter = ('status', 'prioridade', 'setor', 'data_criacao')
    search_fields = ('numero', 'justificativa')
    inlines = [ItemPedidoInline]
    date_hierarchy = 'data_criacao'
    
    # Permite ao Admin ver rapidamente os custos totais (Dashboard Básico)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('solicitante', 'setor')

@admin.register(Cotacao)
class CotacaoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'fornecedor', 'valor_total', 'vencedora')
    list_filter = ('vencedora', 'fornecedor')