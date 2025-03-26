from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/new/', views.create_ticket, name='create_ticket'),
    path('tickets/<int:pk>/update/', views.update_ticket, name='update_ticket'),
    path('dashboard/', views.dashboard, name='dashboard'),
]