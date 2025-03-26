from django import template
from tickets.models import Ticket

register = template.Library()

@register.filter(name='get_status_display')
def get_status_display(status_code):
    """
    Filtro personalizado para mostrar el estado del ticket en español.
    Uso: {{ entry.old_status|get_status_display }}
    """
    status_dict = dict(Ticket.STATUS_CHOICES)
    return status_dict.get(status_code, status_code)

@register.filter(name='get_role_color')
def get_role_color(user):
    """
    Filtro personalizado para asignar un color según el rol del usuario.
    Uso: {{ entry.changed_by|get_role_color }}
    """
    role_colors = {
        'CLIENT': 'bg-info',
        'EMPLOYEE': 'bg-primary',
        'ADMIN': 'bg-warning text-dark',
        'SYSTEM_ADMIN': 'bg-danger'
    }
    return role_colors.get(user.role, 'bg-secondary')