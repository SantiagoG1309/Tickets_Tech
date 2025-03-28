from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Employee, Admin, SystemAdmin, Technician
from tickets.models import Category

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['Usuario', 'Contraseña']

class EmployeeCreationForm(forms.ModelForm):
    department = forms.CharField(label='Departamento',required=True)
    position = forms.CharField(label='Puesto',required=True)
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
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

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
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    assigned_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label=None,
        required=True,
        label='Categoría Asignada'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'assigned_category']
