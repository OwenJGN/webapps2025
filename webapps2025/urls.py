"""
URL configuration for webapps2025 project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Home page without any redirects
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # Application URLs
    path('webapps2025/', include([
        path('', include('register.urls')),
        path('', include('payapp.urls')),
        path('', include('currency_service.urls')),
    ])),
]