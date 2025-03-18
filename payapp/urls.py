from django.urls import path
from . import views
from .currency_service import CurrencyConversionView

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('make-payment/', views.make_payment, name='make_payment'),
    path('request-payment/', views.request_payment, name='request_payment'),
    path('notifications/', views.notifications, name='notifications'),
    path('respond-to-request/<int:request_id>/', views.respond_to_request, name='respond_to_request'),
    path('transactions/', views.transactions, name='transactions'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/transactions/', views.admin_transactions, name='admin_transactions'),
    path('admin/register/', views.register_admin, name='register_admin'),
    path('conversion/<str:from_currency>/<str:to_currency>/<str:amount>/', CurrencyConversionView.as_view(), name='currency_conversion'),
]