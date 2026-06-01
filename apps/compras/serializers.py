import os
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import PedidoCompra, ItemPedido, Cotacao, Aprovacao, Anexo

class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = '__all__'
        read_only_fields = ('pedido',)

class CotacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cotacao
        fields = '__all__'

class AprovacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aprovacao
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True)
    cotacoes = CotacaoSerializer(many=True, read_only=True)
    
    class Meta:
        model = PedidoCompra
        fields = '__all__'
        read_only_fields = ('numero', 'status', 'solicitante', 'data_criacao', 'sla_vencimento')

    def create(self, validated_data):
        itens_data = validated_data.pop('itens', [])
        pedido = PedidoCompra.objects.create(**validated_data)
        for item_data in itens_data:
            ItemPedido.objects.create(pedido=pedido, **item_data)
        return pedido


class AnexoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexo
        fields = ['id', 'arquivo', 'tipo', 'content_type', 'object_id']
        
    def validate_arquivo(self, value):
        ext = os.path.splitext(value.name)[1]
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.xls']
        if not ext.lower() in valid_extensions:
            raise serializers.ValidationError("Formato de ficheiro não suportado. Envie PDF, Imagem ou Excel.")
        
        # Limitar a 5MB
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("O ficheiro excede o tamanho máximo de 5MB.")
            
        return value