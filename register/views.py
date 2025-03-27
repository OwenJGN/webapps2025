from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, UserProfileForm
import requests
from django.conf import settings


def register(request):
    """
    Handle user registration with form validation and profile creation.

    Creates a new user account and profile with the specified currency.
    Sets the initial balance based on the standard amount in GBP,
    converted to their selected currency if necessary.

    Args:
        request: The HTTP request

    Returns:
        HttpResponse: The rendered template or a redirect
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
    Handle user profile viewing and editing.

    Allows users to update their account details and currency preference.
    If the currency is changed, converts their current balance to the new currency.

    Args:
        request: The HTTP request

    Returns:
        HttpResponse: The rendered template or a redirect
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