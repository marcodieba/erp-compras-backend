from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Setor, CentroCusto

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informações ERP', {'fields': ('perfil', 'setor', 'telefone')}),
    )
    list_display = ('username', 'email', 'first_name', 'perfil', 'setor')
    list_filter = ('perfil', 'setor', 'is_staff')

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome')

@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'setor')
    list_filter = ('setor',)