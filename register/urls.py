from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

"""
URL Configuration for the register app.
Includes routes for user registration, authentication, and profile management.
"""

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='register/login.html'), name='login'),
    # Update logout view to accept GET requests
    path('logout/', auth_views.LogoutView.as_view(template_name='register/logout.html', next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
]