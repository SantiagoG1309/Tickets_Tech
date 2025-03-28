from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('create-employee/', views.create_employee, name='create_employee'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('create-system-admin/', views.create_system_admin, name='create_system_admin'),
    path('create-technician/', views.create_technician, name='create_technician'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]