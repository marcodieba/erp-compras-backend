from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, Setor, CentroCusto
from .serializers import UserSerializer, SetorSerializer, CentroCustoSerializer
from .permissions import IsGerente # Apenas Admin/Gerente configuram a base

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    # CORREÇÃO: Nova regra dinâmica de permissões
    def get_permissions(self):
        # Se for apenas para ler (GET), qualquer utilizador autenticado tem permissão
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated()]
        # Se for para criar/editar/apagar (POST, PUT, DELETE), exige ser Gerente/Admin
        return [IsGerente()]

class SetorViewSet(viewsets.ModelViewSet):
    queryset = Setor.objects.all()
    serializer_class = SetorSerializer
    permission_classes = [IsAuthenticated] # Todos podem ler setores na hora de criar pedido

class CentroCustoViewSet(viewsets.ModelViewSet):
    queryset = CentroCusto.objects.all()
    serializer_class = CentroCustoSerializer
    permission_classes = [IsAuthenticated]