from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, Setor, CentroCusto
from .serializers import UserSerializer, SetorSerializer, CentroCustoSerializer
from .permissions import IsGerente # Apenas Admin/Gerente configuram a base

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsGerente]

class SetorViewSet(viewsets.ModelViewSet):
    queryset = Setor.objects.all()
    serializer_class = SetorSerializer
    permission_classes = [IsAuthenticated] # Todos podem ler setores na hora de criar pedido

class CentroCustoViewSet(viewsets.ModelViewSet):
    queryset = CentroCusto.objects.all()
    serializer_class = CentroCustoSerializer
    permission_classes = [IsAuthenticated]