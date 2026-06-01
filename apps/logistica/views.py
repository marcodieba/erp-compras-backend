from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Fornecedor, Rastreamento
from .serializers import FornecedorSerializer, RastreamentoSerializer
from apps.core.permissions import IsComprador, IsGerente

class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    permission_classes = [IsComprador] # Compradores e Gerentes podem gerir fornecedores
    
    # Aqui pode entrar filtros avançados por avaliação e atrasos

class RastreamentoViewSet(viewsets.ModelViewSet):
    queryset = Rastreamento.objects.all()
    serializer_class = RastreamentoSerializer
    permission_classes = [IsComprador]
    
    def perform_update(self, serializer):
        # Sempre que atualiza, o campo ultima_atualizacao é renovado automaticamente pelo auto_now=True
        # Podemos disparar um sinal ou chamada de Service para notificar via WebSocket aqui
        serializer.save()