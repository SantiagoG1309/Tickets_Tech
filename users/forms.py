from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Employee, Admin, SystemAdmin, Technician
from tickets.models import Category

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellido')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña'
        }

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Nombre de usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'password']

class EmployeeCreationForm(forms.ModelForm):
    department = forms.CharField(label='Departamento', required=True)
    position = forms.CharField(label='Puesto', required=True)
    class Meta:
        model = Employee
        fields = ['department', 'position']

class AdminCreationForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = []

class SystemAdminCreationForm(forms.ModelForm):
    class Meta:
        model = SystemAdmin
        fields = []

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    username = forms.CharField(label='Nombre de usuario')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido'
        }

class TechnicianForm(forms.ModelForm):
    assigned_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label=None,
        required=True,
        label='Categoría Asignada'
    )
    
    class Meta:
        model = Technician
        fields = []

class TechnicianUserForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    username = forms.CharField(label='Nombre de usuario')
    assigned_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label=None,
        required=True,
        label='Categoría Asignada'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'assigned_category']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
            'assigned_category': 'Categoría Asignada'
        }
