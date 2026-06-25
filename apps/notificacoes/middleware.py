# apps/notificacoes/middleware.py
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

@database_sync_to_async
def get_user_from_token(token_string):
    # O User só é importado quando a função corre, evitando crashes no arranque
    User = get_user_model() 
    try:
        access_token = AccessToken(token_string)
        return User.objects.get(id=access_token["user_id"])
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware:
    """
    Extrai o token JWT da query string do WebSocket.
    Exemplo no frontend: ws://dominio.com/ws/notificacoes/?token=eyJhbGci...
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_parameters = parse_qs(query_string)
        token = query_parameters.get("token", [None])[0]

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)