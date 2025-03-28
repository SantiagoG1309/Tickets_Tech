from django.db import migrations

def create_categories_and_update_tickets(apps, schema_editor):
    Category = apps.get_model('tickets', 'Category')
    Ticket = apps.get_model('tickets', 'Ticket')
    
    # Crear categorías basadas en los valores existentes
    categories = ['TECHNICAL', 'BILLING', 'GENERAL', 'OTHER']
    
    # Primero, asegurarse de que todas las categorías existan
    for category_name in categories:
        Category.objects.get_or_create(name=category_name)
    
    # Obtener la categoría GENERAL como fallback
    general_category = Category.objects.get(name='GENERAL')
    
    # Actualizar tickets existentes para usar las nuevas categorías
    for ticket in Ticket.objects.all():
        if not ticket.category_id:
            ticket.category = general_category
            ticket.save()

class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0003_category_alter_ticket_category'),
    ]

    operations = [
        migrations.RunPython(create_categories_and_update_tickets),
    ]