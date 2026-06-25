from rest_framework import permissions

class IsGerente(permissions.BasePermission):
    def has_permission(self, request, view):
        # Permite acesso se for Gerente OU se for o Superuser (Admin)
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.perfil == 'GERENTE' or request.user.is_superuser))

class IsComprador(permissions.BasePermission):
    def has_permission(self, request, view):
        # Permite acesso se for Comprador, Gerente OU Superuser
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.perfil in ['COMPRADOR', 'GERENTE'] or request.user.is_superuser))