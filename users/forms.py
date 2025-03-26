from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Employee, Admin, SystemAdmin

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

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
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']