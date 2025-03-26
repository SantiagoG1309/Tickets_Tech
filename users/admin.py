from django.contrib import admin
from .models import User, Employee, Admin, SystemAdmin

# Registrar los modelos en el panel de administración
admin.site.register(User)
admin.site.register(Employee)
admin.site.register(Admin)
admin.site.register(SystemAdmin)
