# Generated by Django 4.2.7 on 2025-03-27 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_alter_category_options_alter_ticket_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='priority',
            field=models.CharField(choices=[('HIGH', 'Urgente'), ('MEDIUM', 'Medio'), ('LOW', 'Bajo')], default='LOW', max_length=10),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='priority',
            field=models.CharField(choices=[('HIGH', 'Urgente'), ('MEDIUM', 'Medio'), ('LOW', 'Bajo')], editable=False, max_length=10),
        ),
    ]
