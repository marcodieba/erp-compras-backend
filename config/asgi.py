import os
from django.core.asgi import get_asgi_application

# Mantém a sua configuração original
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_compras.settings')

# 1. INICIALIZA O DJANGO PRIMEIRO!
django_asgi_app = get_asgi_application()

# 2. Só DEPOIS importamos as rotas e o middleware personalizado
from channels.routing import ProtocolTypeRouter, URLRouter
from apps.notificacoes.routing import websocket_urlpatterns
from apps.notificacoes.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Substituímos o AuthMiddlewareStack pelo nosso JWTAuthMiddleware
    "websocket": JWTAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})