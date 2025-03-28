from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Ticket, Comment, TicketHistory, Category, TechnicianNotification
from .forms import TicketForm, TicketUpdateForm, CommentForm
from users.models import User

def home(request):
    """Home view that shows the landing page for non-authenticated users and dashboard for authenticated users"""
    if not request.user.is_authenticated:
        return render(request, 'home.html')
    
    user = request.user
    
    # Obtener todos los tickets y tickets personales
    all_tickets = Ticket.objects.all().order_by('-created_at')
    personal_tickets = Ticket.objects.filter(created_by=user).order_by('-created_at')
    
    # Si es técnico, mostrar solo tickets de su categoría
    if user.role == 'TECHNICIAN':
        if user.assigned_category:
            all_tickets = all_tickets.filter(category=user.assigned_category)
            # Obtener notificaciones no leídas
            notifications = TechnicianNotification.objects.filter(
                technician=user,
                is_read=False
            ).order_by('-created_at')
        else:
            messages.warning(request, 'No tienes una categoría asignada.')
            notifications = []
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        all_tickets = all_tickets.filter(status=status_filter)
        personal_tickets = personal_tickets.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        all_tickets = all_tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        personal_tickets = personal_tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'tickets': all_tickets,
        'personal_tickets': personal_tickets,
        'status_filter': status_filter,
        'search_query': search_query
    }
    
    if user.role == 'CLIENT':
        return render(request, 'tickets/client_dashboard.html', context)
    elif user.role == 'TECHNICIAN':
        context['notifications'] = notifications
        return render(request, 'tickets/technician_dashboard.html', context)
    elif user.role in ['EMPLOYEE', 'ADMIN', 'SYSTEM_ADMIN']:
        return render(request, 'tickets/staff_dashboard.html', context)
    
    return redirect('login')

@login_required
def ticket_list(request):
    """View to list all tickets based on user role"""
    user = request.user
    
    # Los técnicos solo pueden ver tickets de su categoría
    if user.role == 'TECHNICIAN':
        if user.assigned_category:
            tickets = Ticket.objects.filter(category=user.assigned_category).order_by('-created_at')
        else:
            messages.warning(request, 'No tienes una categoría asignada.')
            tickets = Ticket.objects.none()
    else:
        tickets = Ticket.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        all_tickets = all_tickets.filter(status=status_filter)
        personal_tickets = personal_tickets.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        all_tickets = all_tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        personal_tickets = personal_tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'status_filter': status_filter,
        'search_query': search_query
    })

@login_required
def personal_tickets(request):
    """View to list personal tickets of the current user"""
    user = request.user
    
    # Get only tickets created by the current user
    tickets = Ticket.objects.filter(created_by=user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        all_tickets = all_tickets.filter(status=status_filter)
        personal_tickets = personal_tickets.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        all_tickets = all_tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        personal_tickets = personal_tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    return render(request, 'tickets/personal_tickets.html', {
        'tickets': tickets,
        'status_filter': status_filter,
        'search_query': search_query
    })

@login_required
def ticket_detail(request, pk):
    """View to see details of a specific ticket"""
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Todos los roles pueden ver todos los tickets
    user = request.user
    
    # Si es un técnico, marcar la notificación como leída
    if user.role == 'TECHNICIAN':
        TechnicianNotification.objects.filter(
            technician=user,
            ticket=ticket,
            is_read=False
        ).update(is_read=True)
    
    # Handle comment form
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comentario añadido correctamente.')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        comment_form = CommentForm()
    
    # Get ticket history and comments
    history = ticket.history.all().order_by('-changed_at')
    comments = ticket.comments.all().order_by('-created_at')
    
    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'history': history,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def create_ticket(request):
    """View to create a new ticket"""
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            
            # Ya no se asignan tickets automáticamente
            
            ticket.save()
            
            # Crear notificación para los técnicos de la categoría
            if ticket.category:
                from users.models import User
                technicians = User.objects.filter(role='TECHNICIAN', assigned_category=ticket.category)
                for technician in technicians:
                    TechnicianNotification.objects.create(
                        technician=technician,
                        ticket=ticket
                    )
            messages.success(request, 'Ticket creado correctamente.')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm()
    
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Crear Ticket'})

@login_required
def update_ticket(request, pk):
    """View to update an existing ticket"""
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Check if user has permission to update this ticket
    user = request.user
    
    # Verificar permisos según el rol
    if user.role == 'TECHNICIAN':
        # Verificar si el ticket pertenece a la categoría asignada al técnico
        if not user.assigned_category or user.assigned_category != ticket.category:
            return HttpResponseForbidden("No tienes permiso para actualizar este ticket.")
    elif user.role not in ['ADMIN', 'SYSTEM_ADMIN'] and ticket.created_by != user:
        return HttpResponseForbidden("No tienes permiso para actualizar este ticket.")
    
    # Guardar el estado actual antes de cualquier cambio
    old_status = ticket.status
    
    if request.method == 'POST':
        # Determinar qué campos puede editar según el rol
        if ticket.created_by == user:
            form = TicketForm(request.POST, instance=ticket)
        elif user.role in ['ADMIN', 'SYSTEM_ADMIN']:
            form = TicketUpdateForm(request.POST, instance=ticket)
            form.fields = {'status': form.fields['status']}
        elif user.role == 'TECHNICIAN':
            form = TicketUpdateForm(request.POST, instance=ticket)
            form.fields = {'status': form.fields['status']}
        # Otros roles no deberían llegar aquí debido a la verificación anterior
        
        if form.is_valid():
            # Guardar el ticket sin llamar al método save() del modelo
            ticket = form.save(commit=False)
            
            # Si el estado ha cambiado, crear una entrada en el historial manualmente
            if old_status != ticket.status:
                # Guardar el ticket primero sin crear historial (ya modificamos el método save)
                ticket.save()
                
                # Crear la entrada del historial manualmente
                from .models import TicketHistory
                from django.utils import timezone
                
                # Verificar si ya existe una entrada reciente con el mismo cambio de estado
                # para evitar duplicados
                recent_entries = TicketHistory.objects.filter(
                    ticket=ticket,
                    old_status=old_status,
                    new_status=ticket.status
                ).order_by('-changed_at')[:1]
                
                # Solo crear nueva entrada si no hay una reciente con el mismo cambio
                if not recent_entries or (timezone.now() - recent_entries[0].changed_at).seconds > 10:
                    TicketHistory.objects.create(
                        ticket=ticket,
                        changed_by=user,  # Usar el usuario actual de la solicitud
                        old_status=old_status,
                        new_status=ticket.status,
                        changed_at=timezone.now()
                    )
            else:
                # Si no hay cambio de estado, guardar normalmente
                ticket.save()
                
            messages.success(request, 'Ticket actualizado correctamente. El estado actual es: ' + ticket.get_status_display())
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        # Determinar qué campos puede editar según el rol
        if ticket.created_by == user:
            form = TicketForm(instance=ticket)
        elif user.role in ['ADMIN', 'SYSTEM_ADMIN', 'TECHNICIAN']:
            form = TicketUpdateForm(instance=ticket)
            form.fields = {'status': form.fields['status']}
        # Otros roles no deberían llegar aquí debido a la verificación anterior
    
    return render(request, 'tickets/ticket_form.html', {
        'form': form, 
        'ticket': ticket,
        'title': 'Actualizar Ticket'
    })

@login_required
def dashboard(request):
    """Admin dashboard with reports and statistics"""
    # Only admins and system admins can access the dashboard
    if request.user.role not in ['ADMIN', 'SYSTEM_ADMIN']:
        return HttpResponseForbidden("No tienes permiso para acceder al dashboard.")
    
    # Get personal tickets for the current user
    personal_tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Get statistics for the dashboard
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='OPEN').count()
    in_progress_tickets = Ticket.objects.filter(status='IN_PROGRESS').count()
    resolved_tickets = Ticket.objects.filter(status='RESOLVED').count()
    closed_tickets = Ticket.objects.filter(status='CLOSED').count()
    
    # Get tickets by priority
    high_priority = Ticket.objects.filter(priority='HIGH').count()
    medium_priority = Ticket.objects.filter(priority='MEDIUM').count()
    low_priority = Ticket.objects.filter(priority='LOW').count()
    
    # Get tickets by category
    categories = Category.objects.all()
    tickets_by_category = {}
    for category in categories:
        tickets_by_category[category.name] = Ticket.objects.filter(category=category).count()
    
    # Get recent tickets for the table
    tickets = Ticket.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'tickets_by_category': tickets_by_category,
        'tickets': tickets,
        'personal_tickets': personal_tickets,
        'status_filter': status_filter,
        'categories': categories,
    }
    
    return render(request, 'tickets/dashboard.html', context)


@login_required
def manage_categories(request):
    """View for administrators to manage categories"""
    if request.user.role not in ['ADMIN', 'SYSTEM_ADMIN']:
        return HttpResponseForbidden("No tienes permiso para gestionar categorías.")

    categories = Category.objects.all()

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        priority = request.POST.get('priority')
        if category_name and priority:
            Category.objects.create(name=category_name, priority=priority)
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('manage_categories')

    return render(request, 'tickets/manage_categories.html', {'categories': categories})

@login_required
def delete_category(request, category_id):
    """View for deleting a category"""
    if request.user.role not in ['ADMIN', 'SYSTEM_ADMIN']:
        return HttpResponseForbidden("No tienes permiso para eliminar categorías.")

    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Categoría eliminada correctamente.')
    return redirect('manage_categories')
