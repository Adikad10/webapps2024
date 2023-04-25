from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import SendMoneyForm, RequestMoneyForm
from register.models import Transaction, User, Request
from rest_framework import status
import requests
from currency_conversion.views import CONVERSION_RATES
from currency_conversion.views import get_converted_amount
from django.contrib import messages
from decimal import Decimal

CONVERSION_API_URL = 'http://127.0.0.1:8000/conversion/'


def reset_and_add_balance_to_all_users(base_amount=1000, base_currency='GBP'):
    users = User.objects.filter(is_active=True)
    print(f'{users.count()} active users found')

    for user in users:
        print(f'Updating balance for user {user.username}')
        user.balance = 0

        if user.currency == base_currency:
            user.balance += base_amount
        else:
            conversion_rate = get_conversion_rate(base_currency, user.currency)
            converted_amount = base_amount * conversion_rate
            user.balance += converted_amount
        print(f'New balance for user {user.username}: {user.balance}')
        user.save()


"""
def get_balance(user):
    balance = Decimal('0')
    sent_transactions = user.transactions.all()
    received_transactions = user.received_transactions.all()
    transactions = sent_transactions | received_transactions

    print(f'Calculating balance for user {user.username}:')  # Debugging: Start of balance calculation
    print(f'Sent transactions count: {sent_transactions.count()}')  # Debugging: Sent transactions count
    print(f'Received transactions count: {received_transactions.count()}')  # Debugging: Received transactions count

    for transaction in transactions:
        if transaction.user == user:
            balance -= transaction.amount
            print(f'Sent transaction: {transaction.amount}, Updated balance: {balance}')  # Debugging: Sent transaction and updated balance
        else:
            conversion_rate = get_conversion_rate(transaction.currency, user.currency)
            balance += transaction.amount * conversion_rate
            print(f'Received transaction: {transaction.amount}, Updated balance: {balance}')  # Debugging: Received transaction and updated balance

    user.balance = balance
    user.save()

    print(f'Final balance for user {user.username}: {balance}')  # Debugging: Final balance after calculation

    return balance

"""


def make_payment(sender, recipient, amount, currency):
    if not isinstance(sender, User):
        raise ValueError('Sender must be a User object')
    if not isinstance(recipient, User):
        raise ValueError('Recipient must be a User object')
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError('Amount must be a positive number')
    if not isinstance(currency, str) or len(currency) != 3:
        raise ValueError('Currency must be a 3-letter string code')

    sender_currency = sender.currency
    conversion_rates = CONVERSION_RATES.get(sender_currency, {})

    converted_amount = get_converted_amount(amount, currency, recipient.currency)

    print(f"Sender initial balance: {sender.balance}")  # Debugging: Print sender's initial balance
    if sender.balance < Decimal(amount):  # Convert amount to Decimal
        raise ValueError('Insufficient funds')
    sender.balance -= Decimal(amount)  # Convert amount to Decimal
    sender.save()
    print(f"Sender updated balance: {sender.balance}")  # Debugging: Print sender's updated balance

    print(f"Recipient initial balance: {recipient.balance}")  # Debugging: Print recipient's initial balance
    recipient.balance += Decimal(converted_amount)  # Convert converted_amount to Decimal
    recipient.save()
    print(f"Recipient updated balance: {recipient.balance}")  # Debugging: Print recipient's updated balance

    transaction = Transaction(user=sender, recipient=recipient, amount=Decimal(amount), currency=currency)  # Convert amount to Decimal
    transaction.save()


def get_conversion_rate(currency1='USD', currency2='EUR', amount_of_currency1='1'):
    allowed_currencies = ['USD', 'EUR', 'GBP']
    if currency1 not in allowed_currencies or currency2 not in allowed_currencies:
        raise ValueError('Invalid currency')
    url = f'{CONVERSION_API_URL}{currency1}/{currency2}/{amount_of_currency1}'
    response = requests.get(url)
    if response.status_code == status.HTTP_200_OK:
        try:
            data = response.json()
            return data['conversion_rate']
        except (ValueError, KeyError) as e:
            print(f'Error decoding JSON response: {e}')
    else:
        print(f'Request failed with status code {response.status_code}: {response.content}')
    raise ValueError('Unable to get conversion rate')


def check_balance(request):
    balance = request.user.balance
    return render(request, 'check_balance.html', {'balance': balance})


def check_transactions(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'check_transactions.html', {'transactions': transactions})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    balance = request.user.balance
    print(f'User: {request.user.username}, Balance: {balance}')  # Debugging: Print user's balance

    transactions = Transaction.objects.filter(user=request.user)

    send_money_form = SendMoneyForm()
    request_money_form = RequestMoneyForm()

    money_requests = Request.objects.filter(recipient=request.user)

    if request.method == 'POST':
        if 'send_money' in request.POST:
            send_money_form = SendMoneyForm(request.POST)
            if send_money_form.is_valid():
                sender = request.user
                recipient_email = send_money_form.cleaned_data['recipient_email']
                recipient = User.objects.get(email=recipient_email)
                amount = send_money_form.cleaned_data['amount']
                currency = send_money_form.cleaned_data['currency']

                if amount <= 0:
                    messages.error(request, 'Amount must be a positive number')
                else:
                    make_payment(sender, recipient, amount, currency)
                    print(
                        f'Send Money: Sender: {sender}, Recipient: {recipient}, Amount: {amount}, Currency: {currency}')  # Debugging: Print send money info
                    return redirect('dashboard')

        elif 'request_money' in request.POST:
            request_money_form = RequestMoneyForm(request.POST)
            if request_money_form.is_valid():
                sender_email = request_money_form.cleaned_data['sender_email']
                sender = User.objects.get(email=sender_email)
                recipient = request.user
                amount = request_money_form.cleaned_data['amount']
                currency = request_money_form.cleaned_data['currency']
                message = 'Request for money transfer'
                new_request = Request(user=sender, recipient=recipient, amount=amount, currency=currency,
                                      message=message)
                new_request.save()
                print(
                    f'Request Money: Sender: {sender}, Recipient: {recipient}, Amount: {amount}, Currency: {currency}')  # Debugging: Print request money info
                return redirect('dashboard')

        elif 'approve_request' in request.POST or 'reject_request' in request.POST:
            request_id = request.POST.get('request_id')
            if request_id:
                money_request = Request.objects.get(id=request_id, recipient=request.user)
                if 'approve_request' in request.POST:
                    sender_email = money_request.user.email
                    sender = User.objects.get(email=sender_email)
                    recipient = request.user
                    amount = money_request.amount
                    currency = money_request.currency
                    make_payment(sender, recipient, amount, currency)
                    money_request.status = 'completed'
                    money_request.save()
                    messages.success(request, 'Money request approved and transaction completed')
                elif 'reject_request' in request.POST:
                    money_request.status = 'rejected'
                    money_request.save()
                    messages.success(request, 'Money request rejected')
                else:
                    messages.error(request, 'Invalid action')
                return redirect('dashboard')

    context = {
        'balance': balance,
        'transactions': transactions,
        'send_money_form': send_money_form,
        'request_money_form': request_money_form,
        'money_requests': money_requests,
    }
    return render(request, 'user_dashboard.html', context)
