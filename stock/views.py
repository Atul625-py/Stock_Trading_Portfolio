from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import RegisterForm
from django.contrib.auth.hashers import make_password
from django.db.models import F, ExpressionWrapper, DecimalField
from .models import Stock, Portfolio, Transaction, User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import fetch_and_load_stock_data  # Import your function
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import logout


@csrf_exempt  # Disable CSRF for simplicity, you may want to handle CSRF tokens properly in production
def reload_stocks(request):
    if request.method == 'POST':
        fetch_and_load_stock_data()
        return JsonResponse({'status': 'Stocks reloaded successfully'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


# Create your views here.

def add_transaction(request, portfolio_id):
    if request.method == 'POST':
        portfolio = get_object_or_404(Portfolio, pk=portfolio_id)
        stock_id = request.POST['stock_id']
        quantity = request.POST['quantity']
        price_per_share = request.POST['price_per_share']
        transaction_type = request.POST['transaction_type']
        stock = get_object_or_404(Stock, pk=stock_id)
        Transaction.objects.create(
            portfolio=portfolio,
            stock=stock,
            quantity=quantity,
            price_per_share=price_per_share,
            transaction_type=transaction_type
        )
        return redirect('portfolio', portfolio_id=portfolio.id)
    else:
        stocks = Stock.objects.all()
        return render(request, 'transactions.html', {'stocks': stocks})

@login_required(login_url='/login/')
def home(request):
    user = request.user

    portfolio = Portfolio.objects.filter(user=user).first()  # Ensure to get the portfolio for the current user

    if portfolio:
        transactions = Transaction.objects.filter(
            portfolio=portfolio,
            transaction_type='buy'
        ).select_related('stock')

        transactions = transactions.annotate(
            current_price=F('stock__current_price'),
            total_dividend=ExpressionWrapper(
                F('stock__dividend_amount') * F('quantity'),
                output_field=DecimalField()
            ),
            profit_loss_possible=ExpressionWrapper(
                (F('stock__dividend_amount') + F('stock__current_price') - F('price_per_share')) * F('quantity'),
                output_field=DecimalField()
            )
        )
    else:
        transactions = None

    return render(request, 'stock/home.html', {'transactions': transactions})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful! You can now view home page.")

                return redirect('/home/')  # Redirect to the home page after successful login
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'stock/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password-confirm')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        # Check if passwords match
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'stock/register.html')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'stock/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'stock/register.html')

        # Create the new user
        new_user = User(
            email=email,
            username=username,
            password=password,  # The manager handles password hashing
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        new_user.save() 

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')  # Redirect to login page after successful registration

    return render(request, 'stock/register.html')

def profile(request):
    return render(request, 'stock/profile.html')

def watchlist(request):
    return render(request, 'stock/watchlist.html')


def stocks(request):
    stocks = Stock.objects.all()  # Fetch all stocks from the database
    return render(request, 'stock/stocks.html', {'stocks': stocks})

def portfolio(request):
    return render(request, 'stock/portfolio.html')

def transactions(request):
    return render(request, 'stock/transactions.html')


def user_logout(request):
    logout(request)
    return redirect('login')