from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('CLIENT', 'Cliente'),
        ('EMPLOYEE', 'Empleado'),
        ('ADMIN', 'Administrador'),
        ('SYSTEM_ADMIN', 'Administrador del Sistema'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.username} - {self.position}"

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    
    def __str__(self):
        return self.user.username

class SystemAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='system_admin_profile')
    
    def __str__(self):
        return self.user.username
