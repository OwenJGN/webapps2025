from django.contrib import admin
from .models import Transaction, PaymentRequest

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Transaction model.
    Provides customised list display, filtering and search functionality.
    """
    list_display = ['sender', 'receiver', 'amount_sender_currency', 'sender_currency', 'timestamp', 'transaction_type']
    list_filter = ['timestamp', 'transaction_type', 'sender_currency', 'receiver_currency']
    search_fields = ['sender__username', 'receiver__username', 'description']
    readonly_fields = ['timestamp']

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    """
    Admin configuration for PaymentRequest model.
    Provides customised list display, filtering and search functionality.
    """
    list_display = ['requester', 'requestee', 'amount_requester_currency', 'requester_currency', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'requester_currency']
    search_fields = ['requester__username', 'requestee__username', 'description']
    readonly_fields = ['created_at', 'updated_at']