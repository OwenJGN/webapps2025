import os

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, AdminRegistrationForm, UserProfileForm
from .models import UserProfile
import requests
from django.conf import settings


def register(request):
    """
    Handle user registration
    """
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                # Save the user
                user = user_form.save()

                # Set profile currency
                user.profile.currency = profile_form.cleaned_data.get('currency')

                # Set initial balance based on currency
                initial_amount_gbp = 750.00
                user_currency = user.profile.currency

                if user_currency == 'GBP':
                    user.profile.balance = initial_amount_gbp
                else:
                    # Convert from GBP to user's currency
                    try:

                        response = requests.get(
                            f"{settings.CURRENCY_SERVICE_URL}GBP/{user_currency}/{initial_amount_gbp}",
                            verify=False
                        )

                        if response.status_code == 200:
                            user.profile.balance = response.json().get('converted_amount', initial_amount_gbp)
                        else:
                            user.profile.balance = initial_amount_gbp
                    except Exception:
                        user.profile.balance = initial_amount_gbp

                user.profile.save()

            messages.success(request, f'Your account has been created! You can now log in.')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        profile_form = UserProfileForm()

    return render(request, 'register/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def profile(request):
    """
    Handle user profile view/edit
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            # Get old currency before saving
            old_currency = request.user.profile.currency
            new_currency = profile_form.cleaned_data.get('currency')
            old_balance = request.user.profile.balance

            with transaction.atomic():
                user_form.save()
                profile_form.save()

                # If currency changed, convert balance
                if old_currency != new_currency:
                    try:

                        response = requests.get(
                            f"{settings.CURRENCY_SERVICE_URL}{old_currency}/{new_currency}/{old_balance}",
                            verify=False
                        )
                        if response.status_code == 200:
                            request.user.profile.balance = response.json().get('converted_amount', old_balance)
                            request.user.profile.save()
                    except Exception:
                        # Keep old balance if conversion fails
                        pass

            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'register/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': request.user.profile
    })


# Signal to create initial admin user on application startup
def create_initial_admin():
    """Create initial admin user if no admins exist"""
    if not User.objects.filter(is_staff=True).exists():
        try:
            # Check if username exists first
            if not User.objects.filter(username='admin1').exists():
                # Create admin user
                admin = User.objects.create_user(
                    username='admin1',
                    email='admin1@example.com',
                    password='admin1',
                    first_name='Admin',
                    last_name='User',
                    is_staff=True
                )

                # The profile is created by the signal, just update the balance
                if hasattr(admin, 'profile'):
                    admin.profile.balance = 750.00
                    admin.profile.save()
        except Exception as e:
            print(f"Error creating admin user: {e}")