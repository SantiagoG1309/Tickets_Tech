from django.db import models
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    PRIORITY_CHOICES = (
        ('HIGH', 'Urgente'),
        ('MEDIUM', 'Medio'),
        ('LOW', 'Bajo'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='LOW')

    def __str__(self):
        return self.name

    @staticmethod
    def ensure_general_category():
        Category.objects.get_or_create(name='GENERAL')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Abierto'),
        ('IN_PROGRESS', 'En proceso'),
        ('RESOLVED', 'Resuelto'),
        ('CLOSED', 'Cerrado'),
    )
    
    PRIORITY_CHOICES = (
        ('HIGH', 'Urgente'),
        ('MEDIUM', 'Medio'),
        ('LOW', 'Bajo'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, editable=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_tickets'
    )
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.category:
            self.category = Category.objects.get_or_create(name='GENERAL')[0]
        if self.category:
            self.priority = self.category.priority
        super().save(*args, **kwargs)

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.ticket}"

class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=15, null=True, blank=True)
    new_status = models.CharField(max_length=15)
    changed_at = models.DateTimeField()
    
    def __str__(self):
        old_display = dict(Ticket.STATUS_CHOICES).get(self.old_status, self.old_status) if self.old_status else 'Ninguno'
        new_display = dict(Ticket.STATUS_CHOICES).get(self.new_status, self.new_status)
        return f"Ticket {self.ticket.id} cambió de {old_display} a {new_display}"
    
    def get_old_status_display(self):
        if not self.old_status:
            return 'Ninguno'
        return dict(Ticket.STATUS_CHOICES).get(self.old_status, self.old_status)
    
    def get_new_status_display(self):
        return dict(Ticket.STATUS_CHOICES).get(self.new_status, self.new_status)

class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('RESOLUTION_TIME', 'Tiempo de resolución'),
        ('OPEN_TICKETS', 'Tickets abiertos'),
        ('TEAM_PERFORMANCE', 'Desempeño del equipo'),
    )
    
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.generated_at}"

class TechnicianNotification(models.Model):
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.technician} sobre ticket {self.ticket}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificación de Técnico'
        verbose_name_plural = 'Notificaciones de Técnicos'
