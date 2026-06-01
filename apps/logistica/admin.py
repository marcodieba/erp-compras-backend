from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Fornecedor, Rastreamento

@admin.register(Fornecedor)
class FornecedorAdmin(SimpleHistoryAdmin):
    list_display = ('razao_social', 'cnpj', 'contato_nome', 'nota_avaliacao', 'historico_atrasos')
    search_fields = ('razao_social', 'cnpj')

@admin.register(Rastreamento)
class RastreamentoAdmin(SimpleHistoryAdmin):
    list_display = ('pedido', 'estagio_atual', 'previsao_entrega', 'ultima_atualizacao')
    list_filter = ('estagio_atual',)
    date_hierarchy = 'ultima_atualizacao'