from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment


# Eliminamos la señal pre_save para Member para permitir cambios manuales
# El estado se actualizará desde el Payment o el comando de gestión


@receiver(post_save, sender=Payment)
def update_member_status_after_payment(sender, instance, created, **kwargs):
    """
    Actualiza el estado del miembro después de registrar un pago
    El modelo Payment ya maneja la actualización de membership_expires_at
    """
    if created and instance.member:
        # El estado ya se actualizará en el save() del Payment
        # pero podemos forzar una recarga del miembro para asegurar
        instance.member.refresh_from_db()
