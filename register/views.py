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
    Handle user profile viewing only.

    Users can view their account details but not edit them.
    Admins are redirected to the admin area as they don't have profiles.

    Args:
        request: The HTTP request

    Returns:
        HttpResponse: The rendered template or a redirect
    """
    # Admin users don't have profiles
    if request.user.is_staff:
        messages.info(request, 'Admin accounts do not have user profiles.')
        return redirect('admin_users')

    # If a POST request comes in (which shouldn't happen with the read-only form),
    # redirect to the profile page with a message
    if request.method == 'POST':
        messages.warning(request, 'Profile editing is disabled. Contact an administrator for any account changes.')
        return redirect('profile')

    # Just display the profile read-only
    return render(request, 'register/profile.html', {
        'user': request.user,
        'user_profile': request.user.profile,
        'read_only': True  # Flag to tell the template this is read-only
    })