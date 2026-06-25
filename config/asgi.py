import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.notificacoes.routing import websocket_urlpatterns
from apps.notificacoes.middleware import JWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_compras.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware( # <--- APLICAMOS AQUI
        URLRouter(
            websocket_urlpatterns
        )
    ),
})