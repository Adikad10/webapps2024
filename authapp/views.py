from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from register.models import User
from django.contrib import messages
from payapp.forms import SendMoneyForm, RequestMoneyForm
from payapp.views import make_payment
from currency_conversion.views import get_converted_amount


@login_required
def user_dashboard(request):
    user = request.user
    return render(request, 'user_dashboard.html', context=dict(balance=user.balance))


class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('authapp:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("User is authenticated and logged in.")  # Debugging print statement
            return redirect('authapp:user_dashboard')
        else:
            error_message = "Invalid username or password."
            print(f"Login failed for user: {username}")  # Debugging print statement
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def send_money_view(request):
    if request.method == 'POST':
        send_money_form = SendMoneyForm(request.POST)
        if send_money_form.is_valid():
            sender = request.user
            recipient_email = send_money_form.cleaned_data['recipient_email']
            recipient = User.objects.get(email=recipient_email)
            amount = send_money_form.cleaned_data['amount']
            currency = send_money_form.cleaned_data['currency']
            amount = float(send_money_form.cleaned_data['amount'])
            print("Amount:", amount)
            if amount <= 0:
                messages.error(request, 'Amount must be a positive number')
            else:
                make_payment(sender, recipient, amount, currency)
                messages.success(request, 'Money sent successfully')
                return redirect('dashboard')

    return redirect('dashboard')

@login_required
def request_money_view(request):
    if request.method == 'POST':
        request_money_form = RequestMoneyForm(request.POST)
        if request_money_form.is_valid():
            sender_email = request_money_form.cleaned_data['sender_email']
            sender = User.objects.get(email=sender_email)
            amount = request_money_form.cleaned_data['amount']
            currency = request_money_form.cleaned_data['currency']
            status = request_money_form.cleaned_data['status']
            converted_amount = get_converted_amount(amount, currency, sender.currency)
            request_obj = request.objects.create(
                user=sender,
                recipient=request.user,
                amount=converted_amount,
                currency=currency,
                status=status,
            )
            request_obj.save()
            messages.success(request, 'Money request sent successfully')
            return redirect('dashboard')

    return redirect('dashboard')


@login_required
def approve_money_request(request):
    request_id = request.POST.get('request_id')
    if request_id:
        money_request = request.objects.get(id=request_id, recipient=request.user)
        sender = money_request.user
        recipient = request.user
        amount = money_request.amount
        currency = money_request.currency
        make_payment(sender, recipient, amount, currency)
        money_request.status = 'completed'
        money_request.save()
        messages.success(request, 'Money request approved and transaction completed')
    else:
        messages.error(request, 'Invalid request')

    return redirect('dashboard')


@login_required
def reject_money_request(request):
    request_id = request.POST.get('request_id')
    if request_id:
        money_request = request.objects.get(id=request_id, recipient=request.user)
        money_request.status = 'rejected'
        money_request.save()
        messages.success(request, 'Money request rejected')
    else:
        messages.error(request, 'Invalid request')

    return redirect('dashboard')

