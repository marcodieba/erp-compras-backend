from django.db import models
from apps.core.models import User

class Notificacao(models.Model):
    TIPO_CHOICES = [('INFO', 'Informação'), ('URGENTE', 'Urgente'), ('SLA', 'Alerta SLA')]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='INFO')
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']