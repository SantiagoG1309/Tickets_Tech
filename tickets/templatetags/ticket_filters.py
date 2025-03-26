from django import template

register = template.Library()

@register.filter(name='filter_status')
def filter_by_status(tickets, status_filter):
    """
    Filtro personalizado para filtrar tickets por estado.
    Uso: {{ tickets|filter_status:"status=OPEN" }}
    """
    if not status_filter or not tickets:
        return tickets
    
    # Parsear el filtro (formato: "campo=valor")
    try:
        field, value = status_filter.split('=')
        return [ticket for ticket in tickets if getattr(ticket, field) == value]
    except (ValueError, AttributeError):
        return tickets