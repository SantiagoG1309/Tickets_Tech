from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import SystemAdmin

User = get_user_model()

@receiver(post_save, sender=User)
def assign_system_admin_role(sender, instance, created, **kwargs):
    """
    Asigna automáticamente el rol SYSTEM_ADMIN a los superusuarios
    cuando son creados con el comando createsuperuser
    """
    if created and instance.is_superuser:
        # Asignar el rol SYSTEM_ADMIN al superusuario
        instance.role = 'SYSTEM_ADMIN'
        instance.save(update_fields=['role'])
        
        # Crear el perfil de SystemAdmin para el superusuario
        SystemAdmin.objects.create(user=instance)