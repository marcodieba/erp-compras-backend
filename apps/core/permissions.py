# apps/core/permissions.py
from rest_framework import permissions

class IsGerente(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.perfil in ['GERENTE', 'ADMIN'] or request.user.is_superuser)
        )

class IsComprador(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.perfil in ['COMPRADOR', 'GERENTE', 'ADMIN'] or request.user.is_superuser)
        )

class IsAlmoxarife(permissions.BasePermission):
    def has_permission(self, request, view):
        # Almoxarife é a base, todos os utilizadores autenticados acedem
        return bool(request.user and request.user.is_authenticated)