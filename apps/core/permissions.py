# apps/core/permissions.py
from rest_framework import permissions

class IsGerente(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.perfil in ['GERENTE', 'ADMIN'])

class IsComprador(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.perfil in ['COMPRADOR', 'GERENTE', 'ADMIN'])

class IsAlmoxarife(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated) # Almoxarife é a base, todos acessam algumas rotas dele