from simple_history.signals import pre_create_historical_record
from django.dispatch import receiver
# IMPORTAÇÃO CORRIGIDA AQUI:
from apps.auditoria.middleware import get_current_request

@receiver(pre_create_historical_record)
def pre_create_historical_record_callback(sender, **kwargs):
    history_instance = kwargs['history_instance']
    request = get_current_request()
    
    if request:
        history_instance.history_user = request.user
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Nota de Arquitetura: O campo 'ip_address' deve ser injetado globalmente 
        # nos models do simple_history via settings, mas podemos forçar no objeto subjacente
        if hasattr(history_instance, 'ip_address'):
            history_instance.ip_address = ip