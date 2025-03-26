from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Ticket, Comment, TicketHistory
from .forms import TicketForm, TicketUpdateForm, CommentForm
from users.models import User

@login_required
def home(request):
    """Home view that shows different dashboards based on user role"""
    user = request.user
    
    # Todos los roles pueden ver todos los tickets
    tickets = Ticket.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'search_query': search_query
    }
    
    if user.role == 'CLIENT':
        return render(request, 'tickets/client_dashboard.html', context)
    elif user.role in ['EMPLOYEE', 'ADMIN', 'SYSTEM_ADMIN']:
        return render(request, 'tickets/staff_dashboard.html', context)
    
    return redirect('login')

@login_required
def ticket_list(request):
    """View to list all tickets based on user role"""
    user = request.user
    
    # Ahora todos los roles pueden ver todos los tickets
    tickets = Ticket.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    return render(request, 'tickets/ticket_list.html', {
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
    
    # Solo el creador del ticket puede editarlo
    if ticket.created_by != user and user.role not in ['ADMIN', 'SYSTEM_ADMIN']:
        return HttpResponseForbidden("No tienes permiso para actualizar este ticket.")
    
    # Guardar el estado actual antes de cualquier cambio
    old_status = ticket.status
    
    if request.method == 'POST':
        # Si es el creador del ticket, puede editar todos los campos
        if ticket.created_by == user:
            form = TicketForm(request.POST, instance=ticket)
        # Si es admin o system_admin, solo puede editar el estado
        elif user.role in ['ADMIN', 'SYSTEM_ADMIN']:
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
        # Si es el creador del ticket, puede editar todos los campos
        if ticket.created_by == user:
            form = TicketForm(instance=ticket)
        # Si es admin o system_admin, solo puede editar el estado
        elif user.role in ['ADMIN', 'SYSTEM_ADMIN']:
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
    technical_tickets = Ticket.objects.filter(category='TECHNICAL').count()
    billing_tickets = Ticket.objects.filter(category='BILLING').count()
    general_tickets = Ticket.objects.filter(category='GENERAL').count()
    other_tickets = Ticket.objects.filter(category='OTHER').count()
    
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
        'technical_tickets': technical_tickets,
        'billing_tickets': billing_tickets,
        'general_tickets': general_tickets,
        'other_tickets': other_tickets,
        'tickets': tickets,
        'status_filter': status_filter,
    }
    
    return render(request, 'tickets/dashboard.html', context)
