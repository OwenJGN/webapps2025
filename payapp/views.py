from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from .forms import MakePaymentForm, RequestPaymentForm, RespondToRequestForm
from .models import Transaction, PaymentRequest
from register.forms import AdminRegistrationForm
import requests
from django.conf import settings


@login_required
def dashboard(request):
    """
    Main dashboard view showing user's balance and recent transactions.

    For regular users, displays balance, transactions, and payment options.
    For admin users, only shows admin-specific navigation options.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered dashboard template with context
    """
    # Check if user is admin
    if request.user.is_staff:
        # Redirect admins to the admin dashboard
        return redirect('admin_users')

    # For regular users, proceed with normal dashboard
    # Get user's recent transactions (limit to 5)
    user_transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')[:5]

    # Get user's pending payment requests
    pending_requests = PaymentRequest.objects.filter(
        requestee=request.user,
        status='pending'
    ).order_by('-created_at')

    # Count of pending payment requests for the notification badge
    pending_requests_count = pending_requests.count()

    context = {
        'user_profile': request.user.profile,
        'transactions': user_transactions,
        'pending_requests': pending_requests[:3],  # Show only 3 most recent
        'pending_requests_count': pending_requests_count,
    }

    return render(request, 'payapp/dashboard.html', context)


@login_required
def make_payment(request):
    """
    Handle making direct payments to other users.

    Restricted for admin users who cannot send money.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered form or redirect after successful submission
    """
    # Block admin users from making payments
    if request.user.is_staff:
        messages.error(request, 'Admin users are not allowed to send money.')
        return redirect('admin_users')

    if request.method == 'POST':
        form = MakePaymentForm(request.POST, initial={'sender': request.user})

        if form.is_valid():
            recipient_email = form.cleaned_data.get('recipient_email')
            amount = form.cleaned_data.get('amount')
            description = form.cleaned_data.get('description')

            # Get recipient user
            recipient = User.objects.get(email=recipient_email)

            # Block payments to admin users
            if recipient.is_staff:
                messages.error(request, 'Cannot send money to admin users.')
                return redirect('dashboard')

            # Sender and their currency
            sender = request.user
            sender_currency = sender.profile.currency

            # Recipient and their currency
            recipient_currency = recipient.profile.currency

            # Convert amount to recipient's currency if different
            amount_recipient_currency = amount

            if sender_currency != recipient_currency:
                try:
                    response = requests.get(
                        f"{settings.CURRENCY_SERVICE_URL}{sender_currency}/{recipient_currency}/{amount}",
                        verify=False
                    )
                    if response.status_code == 200:
                        amount_recipient_currency = Decimal(response.json().get('converted_amount', amount))
                except Exception:
                    # Use original amount if conversion fails
                    pass

            with transaction.atomic():
                # Deduct amount from sender
                sender.profile.balance -= amount
                sender.profile.save()

                # Add amount to recipient
                recipient.profile.balance += amount_recipient_currency
                recipient.profile.save()

                # Create transaction record
                Transaction.objects.create(
                    sender=sender,
                    receiver=recipient,
                    amount_sender_currency=amount,
                    amount_receiver_currency=amount_recipient_currency,
                    sender_currency=sender_currency,
                    receiver_currency=recipient_currency,
                    description=description,
                    transaction_type='payment'
                )

            messages.success(request,
                             f'Payment of {sender.profile.get_formatted_balance()[0]}{amount} sent to {recipient.username}!')
            return redirect('dashboard')
    else:
        form = MakePaymentForm(initial={'sender': request.user})

    return render(request, 'payapp/make_payment.html', {'form': form})


@login_required
def request_payment(request):
    """
    Handle requesting payments from other users.

    Restricted for admin users who cannot request money.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered form or redirect after successful submission
    """
    # Block admin users from requesting payments
    if request.user.is_staff:
        messages.error(request, 'Admin users are not allowed to request money.')
        return redirect('admin_users')

    if request.method == 'POST':
        form = RequestPaymentForm(request.POST, initial={'requester': request.user})

        if form.is_valid():
            requestee_email = form.cleaned_data.get('requestee_email')
            amount = form.cleaned_data.get('amount')
            description = form.cleaned_data.get('description')

            # Get requestee user
            requestee = User.objects.get(email=requestee_email)

            # Block requests to admin users
            if requestee.is_staff:
                messages.error(request, 'Cannot request money from admin users.')
                return redirect('dashboard')

            # Requester and their currency
            requester = request.user
            requester_currency = requester.profile.currency

            with transaction.atomic():
                # Create payment request
                PaymentRequest.objects.create(
                    requester=requester,
                    requestee=requestee,
                    amount_requester_currency=amount,
                    requester_currency=requester_currency,
                    description=description,
                    status='pending'
                )

            messages.success(request,
                             f'Payment request of {requester.profile.get_formatted_balance()[0]}{amount} sent to {requestee.username}!')
            return redirect('dashboard')
    else:
        form = RequestPaymentForm(initial={'requester': request.user})

    return render(request, 'payapp/request_payment.html', {'form': form})


@login_required
def notifications(request):
    """
    Show and handle user's payment requests.

    For admin users, redirects to admin panel.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered notifications template with context
    """
    # Block admin users from viewing notifications
    if request.user.is_staff:
        messages.error(request, 'Admin users do not have personal notifications.')
        return redirect('admin_users')

    # Get requests received by the user
    received_requests = PaymentRequest.objects.filter(
        requestee=request.user
    ).order_by('-created_at')

    # Get requests sent by the user
    sent_requests = PaymentRequest.objects.filter(
        requester=request.user
    ).order_by('-created_at')

    return render(request, 'payapp/notifications.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests
    })


@login_required
def respond_to_request(request, request_id):
    """
    Handle responding to a payment request.

    Processes the form submission to accept or reject a payment request.
    If accepted, transfers the money and updates statuses accordingly.
    Displays rounded amounts to users in success messages.

    Args:
        request: The HTTP request object
        request_id: The ID of the payment request to respond to

    Returns:
        HttpResponse: Rendered form or redirect after successful submission
    """
    # Block admin users from responding to requests
    if request.user.is_staff:
        messages.error(request, 'Admin users cannot respond to payment requests.')
        return redirect('admin_users')

    payment_request = get_object_or_404(PaymentRequest, id=request_id, requestee=request.user, status='pending')

    if request.method == 'POST':
        form = RespondToRequestForm(request.POST, initial={'user': request.user})

        if form.is_valid():
            action = form.cleaned_data.get('action')

            with transaction.atomic():
                if action == 'accept':
                    # Get currency information
                    requester = payment_request.requester
                    requestee = request.user
                    requester_currency = payment_request.requester_currency
                    requestee_currency = requestee.profile.currency

                    # Amount in requester's currency
                    amount_requester_currency = payment_request.amount_requester_currency

                    # Convert amount to requestee's currency
                    amount_requestee_currency = amount_requester_currency
                    if requester_currency != requestee_currency:
                        try:
                            response = requests.get(
                                f"{settings.CURRENCY_SERVICE_URL}{requester_currency}/{requestee_currency}/{amount_requester_currency}",
                                verify=False
                            )
                            if response.status_code == 200:
                                amount_requestee_currency = Decimal(
                                    response.json().get('converted_amount', amount_requester_currency))
                        except Exception:
                            # Use original amount if conversion fails
                            pass

                    # Deduct amount from requestee
                    requestee.profile.balance -= amount_requestee_currency
                    requestee.profile.save()

                    # Add amount to requester
                    requester.profile.balance += amount_requester_currency
                    requester.profile.save()

                    # Create transaction record
                    transaction_obj = Transaction.objects.create(
                        sender=requestee,
                        receiver=requester,
                        amount_sender_currency=amount_requestee_currency,
                        amount_receiver_currency=amount_requester_currency,
                        sender_currency=requestee_currency,
                        receiver_currency=requester_currency,
                        description=payment_request.description,
                        transaction_type='request_accepted',
                        payment_request=payment_request
                    )

                    # Update payment request status
                    payment_request.status = 'accepted'
                    payment_request.save()

                    # Format the amount for display with currency symbol and 2 decimal places
                    currency_symbol = '£' if requestee_currency == 'GBP' else '$' if requestee_currency == 'USD' else '€' if requestee_currency == 'EUR' else ''
                    formatted_amount = f"{currency_symbol}{float(amount_requestee_currency):.2f}"

                    messages.success(request, f'Payment request accepted and {formatted_amount} sent!')

                elif action == 'reject':
                    # Update payment request status
                    payment_request.status = 'rejected'
                    payment_request.save()

                    messages.info(request, f'Payment request rejected.')

            return redirect('notifications')
    else:
        form = RespondToRequestForm(initial={'request_id': payment_request.id, 'user': request.user})

    # Convert requested amount to user's currency if needed
    requested_amount = payment_request.amount_requester_currency
    requester_currency = payment_request.requester_currency
    user_currency = request.user.profile.currency

    if requester_currency != user_currency:
        try:
            response = requests.get(
                f"{settings.CURRENCY_SERVICE_URL}{requester_currency}/{user_currency}/{requested_amount}",
                verify=False
            )
            if response.status_code == 200:
                converted_amount = Decimal(response.json().get('converted_amount', requested_amount))
                payment_request.converted_amount = converted_amount
                payment_request.user_currency = user_currency
        except Exception:
            # Use original amount if conversion fails
            payment_request.converted_amount = requested_amount
            payment_request.user_currency = requester_currency
    else:
        payment_request.converted_amount = requested_amount
        payment_request.user_currency = user_currency

    return render(request, 'payapp/respond_to_request.html', {
        'form': form,
        'payment_request': payment_request
    })

@login_required
def transactions(request):
    """
    Show user's transaction history.

    For admin users, redirects to admin transactions view.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered transactions template with context
    """
    # For admin users, redirect to admin transactions view
    if request.user.is_staff:
        return redirect('admin_transactions')

    # Get all transactions involving the user
    user_transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')

    return render(request, 'payapp/transactions.html', {
        'transactions': user_transactions
    })


@login_required
def admin_users(request):
    """
    Admin view to see all user accounts.

    Displays a list of all users with their account information.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered admin users template or redirect if not authorised
    """
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    # Get all users with their profiles
    users = User.objects.all().select_related('profile')

    return render(request, 'payapp/admin/users.html', {
        'users': users
    })


@login_required
def admin_transactions(request):
    """
    Admin view to see all transactions.

    Displays a list of all transactions in the system.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered admin transactions template or redirect if not authorised
    """
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    # Get all transactions
    transactions = Transaction.objects.all().order_by('-timestamp')

    return render(request, 'payapp/admin/transactions.html', {
        'transactions': transactions
    })


@login_required
def register_admin(request):
    """
    Handle admin registration.

    Processes the form submission to create a new administrator account.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered form or redirect after successful submission
    """
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create admin user
                admin = form.save()

                # Set initial balance to 0 for admin users
                admin.profile.balance = 0
                admin.profile.save()

            messages.success(request, f'Admin account has been created!')
            return redirect('admin_users')
    else:
        form = AdminRegistrationForm()

    return render(request, 'payapp/admin/register_admin.html', {'form': form})