import os

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import requests
from django.conf import settings


class Transaction(models.Model):
    """
    Model to store payment transactions between users
    """
    TRANSACTION_TYPES = [
        ('payment', 'Direct Payment'),
        ('request_accepted', 'Payment Request Accepted'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount_sender_currency = models.DecimalField(max_digits=10, decimal_places=2)
    amount_receiver_currency = models.DecimalField(max_digits=10, decimal_places=2)
    sender_currency = models.CharField(max_length=3)
    receiver_currency = models.CharField(max_length=3)
    description = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='payment')
    payment_request = models.ForeignKey('PaymentRequest', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='resulting_transaction')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sender.username} paid {self.receiver.username} {self.amount_sender_currency} {self.sender_currency}"

    def get_sender_amount_display(self):
        """Returns formatted amount with currency symbol for sender"""
        if self.sender_currency == 'GBP':
            return f"£{self.amount_sender_currency:.2f}"
        elif self.sender_currency == 'USD':
            return f"${self.amount_sender_currency:.2f}"
        elif self.sender_currency == 'EUR':
            return f"€{self.amount_sender_currency:.2f}"
        return f"{self.amount_sender_currency:.2f}"

    def get_receiver_amount_display(self):
        """Returns formatted amount with currency symbol for receiver"""
        if self.receiver_currency == 'GBP':
            return f"£{self.amount_receiver_currency:.2f}"
        elif self.receiver_currency == 'USD':
            return f"${self.amount_receiver_currency:.2f}"
        elif self.receiver_currency == 'EUR':
            return f"€{self.amount_receiver_currency:.2f}"
        return f"{self.amount_receiver_currency:.2f}"


class PaymentRequest(models.Model):
    """
    Model to store payment requests between users
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    amount_requester_currency = models.DecimalField(max_digits=10, decimal_places=2)
    requester_currency = models.CharField(max_length=3)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requester.username} requested {self.amount_requester_currency} {self.requester_currency} from {self.requestee.username}"

    def get_amount_display(self):
        """Returns formatted amount with currency symbol"""
        if self.requester_currency == 'GBP':
            return f"£{self.amount_requester_currency:.2f}"
        elif self.requester_currency == 'USD':
            return f"${self.amount_requester_currency:.2f}"
        elif self.requester_currency == 'EUR':
            return f"€{self.amount_requester_currency:.2f}"
        return f"{self.amount_requester_currency:.2f}"

    def get_amount_in_requestee_currency(self):
        """
        Converts the requested amount to the requestee's currency
        """
        from_currency = self.requester_currency
        to_currency = self.requestee.profile.currency

        if from_currency == to_currency:
            return self.amount_requester_currency

        try:
            response = requests.get(
                f"{settings.CURRENCY_SERVICE_URL}{from_currency}/{to_currency}/{self.amount_requester_currency}",
                verify = False
            )
            if response.status_code == 200:
                return response.json().get('converted_amount')
        except Exception:
            pass

        # Return original amount if conversion fails
        return self.amount_requester_currency