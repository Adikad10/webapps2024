from .models import User, Transaction, Request
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from .forms import RegistrationForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from register.decorators import admin_required
from register.models import CustomUser, Transaction

@login_required
@admin_required
def admin_dashboard(request):
    users = CustomUser.objects.all()
    transactions = Transaction.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users, 'transaction': transactions})


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Do not save the user object yet
            user.currency = form.cleaned_data['currency']  # Add the currency field
            user.save()  # Save the user object
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def add_user(request):
    if request.method == 'POST':
        print("Form submitted")
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        currency = request.POST.get('currency')

        # Perform validation on the input
        if not all([username, first_name, last_name, email, password, currency]):
            return HttpResponse("All fields are required")

        # Check for duplicate username
        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists")

        # Check for duplicate email
        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already exists")

        # Create a new User object and save it to the database
        new_user = User(username=username, first_name=first_name, last_name=last_name,
                        email=email, password=password, currency=currency)
        print("User object created:", new_user)  # Add this line
        new_user.save()
        print("User object saved")  # Add this line
        return HttpResponse("User added successfully")

    else:
        # Render a form to add a new user
        return render(request, 'add_user.html')


def add_transaction(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)

        # Get the transaction details from the POST request
        amount = request.POST.get('amount')
        description = request.POST.get('description')

        # Perform validation on the input
        if not all([amount, description]):
            return HttpResponse("All fields are required")

        # Create a new Transaction object and save it to the database
        new_transaction = Transaction(user=user, amount=amount, description=description)
        new_transaction.save()

        return HttpResponse("Transaction added successfully")

    else:
        # Render a form to add a new transaction
        return render(request, 'add_transaction.html')


def add_request(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)

        # Get the request details from the POST request
        amount = request.POST.get('amount')
        description = request.POST.get('description')

        # Perform validation on the input
        if not all([amount, description]):
            return HttpResponse("All fields are required")

        # Create a new Request object and save it to the database
        new_request = Request(user=user, amount=amount, description=description)
        new_request.save()

        return HttpResponse("Request added successfully")

    else:
        # Render a form to add a new request
        return render(request, 'add_request.html')


def get_user(request, user_id):
    user = User.objects.get(id=user_id)
    print(user)
    data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'balance': user.balance,
    }
    return JsonResponse(data)
