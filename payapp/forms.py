import os

from django import forms
from django.contrib.auth.models import User
from .models import Transaction, PaymentRequest
from decimal import Decimal
import requests
from django.conf import settings


class MakePaymentForm(forms.Form):
    """
    Form for making direct payments to other users
    """
    recipient_email = forms.EmailField(label="Recipient's Email")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    description = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def clean_recipient_email(self):
        """Validate that the recipient exists and is not the sender"""
        email = self.cleaned_data.get('recipient_email')

        # Check if user exists
        try:
            recipient = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("No user with this email address exists.")

        # Check if user is trying to pay themselves
        if self.initial.get('sender') == recipient:
            raise forms.ValidationError("You cannot send money to yourself.")

        return email

    def clean_amount(self):
        """Validate that the amount is positive and within range"""
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")

        # Check if sender has sufficient funds
        sender = self.initial.get('sender')
        if sender:
            if amount > sender.profile.balance:
                raise forms.ValidationError("Insufficient funds in your account.")

        return amount


class RequestPaymentForm(forms.Form):
    """
    Form for requesting payments from other users
    """
    requestee_email = forms.EmailField(label="Request From (Email)")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    description = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def clean_requestee_email(self):
        """Validate that the requestee exists and is not the requester"""
        email = self.cleaned_data.get('requestee_email')

        # Check if user exists
        try:
            requestee = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("No user with this email address exists.")

        # Check if user is trying to request from themselves
        if self.initial.get('requester') == requestee:
            raise forms.ValidationError("You cannot request money from yourself.")

        return email

    def clean_amount(self):
        """Validate that the amount is positive and within range"""
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")

        return amount


class RespondToRequestForm(forms.Form):
    """
    Form for responding to payment requests (accept/reject)
    """
    CHOICES = [
        ('accept', 'Accept and Pay'),
        ('reject', 'Reject Request')
    ]

    action = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    request_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean(self):
        """Validate that the user has sufficient funds if accepting"""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        request_id = cleaned_data.get('request_id')

        if action == 'accept':
            try:
                payment_request = PaymentRequest.objects.get(id=request_id)
                user = self.initial.get('user')

                # Convert requested amount to user's currency
                requested_amount_in_user_currency = Decimal('0')

                # If currencies are different, convert
                if payment_request.requester_currency != user.profile.currency:
                    try:

                        response = requests.get(
                            f"{settings.CURRENCY_SERVICE_URL}{payment_request.requester_currency}/{user.profile.currency}/{payment_request.amount_requester_currency}",
                            verify=False
                        )
                        if response.status_code == 200:
                            requested_amount_in_user_currency = Decimal(response.json().get('converted_amount', 0))
                        else:
                            # Default to the original amount if conversion fails
                            requested_amount_in_user_currency = payment_request.amount_requester_currency
                    except Exception:
                        # Default to the original amount if request fails
                        requested_amount_in_user_currency = payment_request.amount_requester_currency
                else:
                    requested_amount_in_user_currency = payment_request.amount_requester_currency

                # Check if user has sufficient funds
                if user.profile.balance < requested_amount_in_user_currency:
                    self.add_error('action', "Insufficient funds to accept this payment request.")

            except PaymentRequest.DoesNotExist:
                self.add_error('request_id', "Invalid payment request.")

        return cleaned_data