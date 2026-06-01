from rest_framework import serializers
from .models import Fornecedor, Rastreamento

class FornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = '__all__'

class RastreamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rastreamento
        fields = '__all__'
        read_only_fields = ('ultima_atualizacao',)