from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
# Importações de Compras
from apps.compras.views import PedidoViewSet, CotacaoViewSet, AprovacaoViewSet, RelatorioViewSet, AnexoViewSet, ItemPedidoViewSet, DashboardViewSet
# Importações de Core
from apps.core.views import UserViewSet, SetorViewSet, CentroCustoViewSet
# Importações de Logística
from apps.logistica.views import FornecedorViewSet, RastreamentoViewSet
# Importações de Notificações
from apps.notificacoes.views import NotificacaoViewSet

router = DefaultRouter()
# Rotas Compras
router.register(r'pedidos', PedidoViewSet)
router.register(r'itens', ItemPedidoViewSet) # NOVO ENDPOINT DE ITENS
router.register(r'cotacoes', CotacaoViewSet)
router.register(r'aprovacoes', AprovacaoViewSet, basename='aprovacoes')
router.register(r'relatorios', RelatorioViewSet, basename='relatorios')
router.register(r'anexos', AnexoViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard') # NOVO ENDPOINT DE DASHBOARD

# Rotas Core (Utilizadores e Estrutura)
router.register(r'usuarios', UserViewSet)
router.register(r'setores', SetorViewSet)
router.register(r'centros-custo', CentroCustoViewSet)

# Rotas Logística
router.register(r'fornecedores', FornecedorViewSet)
router.register(r'rastreamento', RastreamentoViewSet)

# Rotas Notificações
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacoes')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Swagger / OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Endpoints de Autenticação JWT
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_login'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints da API principal
    path('api/v1/', include(router.urls)),
]