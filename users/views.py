from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import UserRegisterForm, UserLoginForm, EmployeeCreationForm, AdminCreationForm, SystemAdminCreationForm, UserUpdateForm, TechnicianUserForm
from .models import User, Employee, Admin, SystemAdmin, Technician

def register(request):
    """View for client registration"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'CLIENT'  # Set role to CLIENT for self-registration
            user.save()
            messages.success(request, f'¡Cuenta creada para {user.username}! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    """Custom login view"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'TECHNICIAN':
                    from django.utils import timezone
                    from tickets.models import Ticket
                    technician = user.technician_profile
                    last_login = technician.last_login_at
                    new_tickets = Ticket.objects.filter(
                        category=user.assigned_category,
                        created_at__gt=last_login if last_login else timezone.now()
                    ).count()
                    if new_tickets > 0:
                        messages.info(request, f'Mientras no estuviste se crearon {new_tickets} tickets con tu categoría')
                    technician.last_login_at = timezone.now()
                    technician.save()
                messages.success(request, f'¡Bienvenido, {username}! ({user.get_role_display()})')
                return redirect('home')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})

@login_required
def create_technician(request):
    if not request.user.role in ['ADMIN', 'SYSTEM_ADMIN']:
        messages.error(request, 'No tienes permiso para crear técnicos')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TechnicianUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'TECHNICIAN'
            user.assigned_category = form.cleaned_data['assigned_category']
            user.save()
            
            technician = Technician(user=user)
            technician.save()
            
            messages.success(request, 'Técnico creado exitosamente')
            return redirect('dashboard')
    else:
        form = TechnicianUserForm()
    
    return render(request, 'users/create_technician.html', {'form': form})

@login_required
def user_list(request):
    """View to list all users (for admins only)"""
    if request.user.role not in ['ADMIN', 'SYSTEM_ADMIN']:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    
    # Obtener parámetros de filtrado
    role_filter = request.GET.get('role')
    search_query = request.GET.get('search')
    
    # Filtrar usuarios
    users = User.objects.all()
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if search_query:
        users = users.filter(
            models.Q(username__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query)
        )
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query
    }
    
    return render(request, 'users/user_list.html', context)

@login_required
def create_employee(request):
    """View to create a new employee (for admins only)"""
    if request.user.role not in ['ADMIN', 'SYSTEM_ADMIN']:
        return HttpResponseForbidden("No tienes permiso para crear empleados.")
    
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        employee_form = EmployeeCreationForm(request.POST)
        
        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'EMPLOYEE'
            user.save()
            
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()
            
            messages.success(request, f'Empleado {user.username} creado correctamente.')
            return redirect('user_list')
    else:
        user_form = UserRegisterForm()
        employee_form = EmployeeCreationForm()
    
    return render(request, 'users/create_employee.html', {
        'user_form': user_form,
        'employee_form': employee_form
    })

@login_required
def create_admin(request):
    """View to create a new admin (for system admins and admins)"""
    if request.user.role not in ['SYSTEM_ADMIN', 'ADMIN']:
        return HttpResponseForbidden("No tienes permiso para crear administradores.")
    
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        admin_form = AdminCreationForm(request.POST)
        
        if user_form.is_valid() and admin_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'ADMIN'
            user.save()
            
            admin = admin_form.save(commit=False)
            admin.user = user
            admin.save()
            
            messages.success(request, f'Administrador {user.username} creado correctamente.')
            return redirect('user_list')
    else:
        user_form = UserRegisterForm()
        admin_form = AdminCreationForm()
    
    return render(request, 'users/create_admin.html', {
        'user_form': user_form,
        'admin_form': admin_form
    })

@login_required
def create_system_admin(request):
    """View to create a new system admin (for system admins only)"""
    if request.user.role != 'SYSTEM_ADMIN':
        return HttpResponseForbidden("No tienes permiso para crear administradores del sistema.")
    
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        system_admin_form = SystemAdminCreationForm(request.POST)
        
        if user_form.is_valid() and system_admin_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'SYSTEM_ADMIN'
            user.save()
            
            system_admin = system_admin_form.save(commit=False)
            system_admin.user = user
            system_admin.save()
            
            messages.success(request, f'Administrador del sistema {user.username} creado correctamente.')
            return redirect('user_list')
    else:
        user_form = UserRegisterForm()
        system_admin_form = SystemAdminCreationForm()
    
    return render(request, 'users/create_system_admin.html', {
        'user_form': user_form,
        'system_admin_form': system_admin_form
    })

@login_required
def edit_user(request, user_id):
    """View to edit a user (for admins and system admins only)"""
    if request.user.role not in ['ADMIN', 'SYSTEM_ADMIN']:
        return HttpResponseForbidden("No tienes permiso para editar usuarios.")
    
    user_to_edit = get_object_or_404(User, id=user_id)
    
    # Verificar permisos: los administradores no pueden editar a otros administradores o superadmins
    if request.user.role == 'ADMIN' and user_to_edit.role in ['ADMIN', 'SYSTEM_ADMIN']:
        return HttpResponseForbidden("No tienes permiso para editar a este usuario.")
    
    # Inicializar formulario específico del rol
    role_form = None
    role_instance = None
    
    # Obtener la instancia específica del rol si existe
    if user_to_edit.role == 'EMPLOYEE':
        try:
            role_instance = Employee.objects.get(user=user_to_edit)
            role_form = EmployeeCreationForm(instance=role_instance)
        except Employee.DoesNotExist:
            role_form = EmployeeCreationForm()
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user_to_edit)
        
        # Manejar formulario específico del rol si existe
        if user_to_edit.role == 'EMPLOYEE':
            role_form = EmployeeCreationForm(request.POST, instance=role_instance)
            if user_form.is_valid() and (role_form is None or role_form.is_valid()):
                user_form.save()
                
                if role_form:
                    employee = role_form.save(commit=False)
                    employee.user = user_to_edit
                    employee.save()
                
                messages.success(request, f'Usuario {user_to_edit.username} actualizado correctamente.')
                return redirect('user_list')
        else:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, f'Usuario {user_to_edit.username} actualizado correctamente.')
                return redirect('user_list')
    else:
        user_form = UserUpdateForm(instance=user_to_edit)
    
    return render(request, 'users/edit_user.html', {
        'user_form': user_form,
        'role_form': role_form,
        'user_to_edit': user_to_edit
    })

@login_required
def delete_user(request, user_id):
    """View to delete a user (for admins and system admins only)"""
    if request.user.role not in ['ADMIN', 'SYSTEM_ADMIN']:
        return HttpResponseForbidden("No tienes permiso para eliminar usuarios.")
    
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Verificar permisos: los administradores no pueden eliminar a superadmins
    if request.user.role == 'ADMIN' and user_to_delete.role == 'SYSTEM_ADMIN':
        return HttpResponseForbidden("No tienes permiso para eliminar a este usuario.")
    
    if request.method == 'POST':
        # Eliminar el usuario
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'Usuario {username} eliminado correctamente.')
        return redirect('user_list')
    
    return render(request, 'users/delete_user.html', {
        'user_to_delete': user_to_delete
    })
