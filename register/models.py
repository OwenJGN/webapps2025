from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
from django.conf import settings


class UserProfile(models.Model):
    """
    Extension of the User model to include currency preference and account balance.
    Each user has one profile with their selected currency and current balance.
    Admin users have empty currency and zero balance.
    """
    CURRENCY_CHOICES = [
        ('GBP', 'GB Pounds (£)'),
        ('USD', 'US Dollars ($)'),
        ('EUR', 'Euros (€)'),
        ('', 'No Currency (Admin)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation of the user profile."""
        if self.user.is_staff:
            return f"{self.user.username}'s admin profile"
        return f"{self.user.username}'s profile ({self.get_currency_display()})"

    def get_formatted_balance(self):
        """
        Return the balance with the appropriate currency symbol.

        Returns:
            str: Formatted balance with currency symbol (e.g., '£50.00')
        """
        # For admin users or empty currency
        if self.user.is_staff or not self.currency:
            return f"N/A"

        if self.currency == 'GBP':
            return f"£{self.balance:.2f}"
        elif self.currency == 'USD':
            return f"${self.balance:.2f}"
        elif self.currency == 'EUR':
            return f"€{self.balance:.2f}"
        return f"{self.balance:.2f}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a UserProfile when a User is created.
    Sets up the initial balance based on their selected currency for regular users,
    or zero balance and no currency for admins.

    Args:
        sender: The model class that sent the signal
        instance: The actual User instance being saved
        created: Boolean; True if a new record was created
    """
    if created:
        # Default initial amount in GBP
        initial_amount_gbp = 750.00

        # Create profile with appropriate settings based on user type
        if not hasattr(instance, 'profile'):
            if instance.is_staff:
                # Admin users get zero balance and no currency
                profile = UserProfile.objects.create(
                    user=instance,
                    currency='',
                    balance=0.00
                )
            else:
                # Regular users get initial balance in their selected currency
                profile = UserProfile.objects.create(user=instance)

                # Set the initial balance according to the currency
                if profile.currency == 'GBP':
                    profile.balance = initial_amount_gbp
                else:
                    # Convert from GBP to the user's chosen currency
                    try:
                        response = requests.get(
                            f"{settings.CURRENCY_SERVICE_URL}GBP/{profile.currency}/{initial_amount_gbp}",
                            verify=False
                        )
                        if response.status_code == 200:
                            profile.balance = response.json().get('converted_amount', initial_amount_gbp)
                        else:
                            # Default to initial amount if conversion fails
                            profile.balance = initial_amount_gbp
                    except Exception:
                        # Default to initial amount if request fails
                        profile.balance = initial_amount_gbp

                profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the UserProfile when the User is saved.

    Args:
        sender: The model class that sent the signal
        instance: The actual User instance being saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()