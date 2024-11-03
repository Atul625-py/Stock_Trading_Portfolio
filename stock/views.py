from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import RegisterForm, UserUpdateForm
from django.contrib.auth.hashers import make_password
from django.db.models import F, ExpressionWrapper, DecimalField
from .models import Stock, Portfolio, Transaction, User, Watchlist, Payment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import fetch_and_load_stock_data, make_graph, fetch_stock_data, generate_stock_graph  
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from decimal import Decimal
import stripe
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator



stripe.api_key = settings.STRIPE_SECRET_KEY



@login_required(login_url='/login/')
def profile(request):
    user = get_object_or_404(User, email=request.user.email)
    portfolio = get_object_or_404(Portfolio, user=user)

    current_wallet_value = user.budget 

    if request.method == 'POST':
        if 'wallet' in request.POST:
            new_wallet_value = request.POST.get('wallet', None)
            if new_wallet_value != current_wallet_value:
                messages.success(request, "Redirecting to payment page.")
                return redirect('../payment/')
            else:
                messages.info(request, "No changes made to the wallet.")


        if 'image' in request.FILES:
            user.image = request.FILES['image']
            user.save()
            return redirect('profile')
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = UserUpdateForm(instance=user)

    context = {
        'user': user,
        'portfolio': portfolio,
        'form': form,
    }
    return render(request, 'stock/profile.html', context)


@login_required(login_url='/login/')
def watchlist(request):
    user = request.user
    watchlist_items = Watchlist.objects.filter(user=user).select_related('stock')

    return render(request, 'stock/watchlist.html', {'watchlist_items': watchlist_items})


def stocks(request):
    stocks = Stock.objects.all()
    paginator = Paginator(stocks, 20)  
    page_number = request.GET.get('page')  
    stocks = paginator.get_page(page_number) 
    start_number = (stocks.number - 1) * paginator.per_page + 1
    return render(request, 'stock/stocks.html', {'stocks': stocks, 'paginator': paginator, 'start_number': start_number})


@login_required(login_url='/login/')
def portfolio(request):


    user = get_object_or_404(User, email=request.user.email)
    portfolio = get_object_or_404(Portfolio, user=user)
    transactions = Transaction.objects.filter(portfolio=portfolio)
    
    total_investment = sum(
        tx.price_per_share * tx.quantity
        for tx in transactions
        if tx.transaction_type in ('buy', 'bs')
    )

    total_investment_pnl = sum(
        tx.price_per_share * tx.quantity
        for tx in transactions
        if tx.transaction_type in ('bs')
    )
    portfolio.profit_loss = 0
    for transaction in transactions:
        if transaction.transaction_type in ('sell'):
            portfolio.profit_loss += transaction.total_price
        elif transaction.transaction_type in ('bs'):
            portfolio.profit_loss -= transaction.total_price

    total_profit_loss = portfolio.profit_loss 
    portfolio.save()

    context = {
        'user': user,
        'portfolio': portfolio,
        'transactions': transactions,
        'total_profit_loss': total_profit_loss,
        'total_investment': total_investment,
        'total_profit_loss_percentage': ((total_profit_loss/total_investment_pnl)*100 if total_investment_pnl != 0 else 0)
    }
    return render(request, 'stock/portfolio.html', context)

@login_required(login_url='/login/')
def transactions(request):
    transactions = Transaction.objects.filter(portfolio__user=request.user).select_related('stock')
    context = {
        'transactions': transactions
    }
    return render(request, 'stock/transactions.html', context)


def user_logout(request):
    logout(request)
    return redirect('login')



@csrf_exempt  
def reload_stocks(request):
    if request.method == 'POST':
        fetch_and_load_stock_data()
        return JsonResponse({'status': 'Stocks reloaded successfully'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required(login_url='/login/')
def home(request):
    user = request.user

    portfolio = Portfolio.objects.filter(user=user).first()  

    if portfolio:
        transactions = Transaction.objects.filter(
            portfolio=portfolio,
            transaction_type='buy'
        ).select_related('stock')

        transactions = transactions.annotate(
            current_price=F('stock__current_price'),
            total_dividend=ExpressionWrapper(
                F('stock__dividend__dividend_amount') * F('quantity'),
                output_field=DecimalField()
            ),
            profit_loss_possible=ExpressionWrapper(
                (F('stock__current_price') - F('price_per_share')) * F('quantity'),
                output_field=DecimalField()
            )
        )
    else:
        transactions = None

    return render(request, 'stock/home.html', {'transactions': transactions})

def login(request):
    if request.method == 'POST':
        
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)

        if (User.objects.filter(username=username).exists()) == False:
            messages.error(request, "Invalid Username")
            return render(request, 'stock/login.html')
        user = User.objects.get(username=username)
        
        user_password = User.objects.get(username=username).password
        if user_password == password:
            auth_login(request, user)
            return redirect(home) 
        else:
            messages.error(request, "Invalid password.")
        
    else:
        form = AuthenticationForm()
    
    return render(request, 'stock/login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password-confirm')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

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
            password=password,  
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        new_user.save() 
        new_portfolio = Portfolio(
            user = new_user

        )
        new_portfolio.save()

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')  

    return render(request, 'stock/register.html')



@login_required(login_url='/login/')
@csrf_exempt
def purchase_stock(request):
    if request.method == 'POST':
        stock_id = request.POST.get('stock_id')
        quantity = int(request.POST.get('quantity'))

        stock = get_object_or_404(Stock, id=stock_id)
        portfolio = get_object_or_404(Portfolio, user=request.user)

        if quantity > stock.quantity:
            return JsonResponse({'status': 'Not enough stock available to complete the purchase.'}, status=400)

        total_price = Decimal(quantity) * stock.current_price

        if total_price > portfolio.user.budget:
            return JsonResponse({'status': 'Not enough budget to complete the purchase.'}, status=400)

        stock.quantity -= quantity
        stock.save()

        portfolio.user.budget -= total_price
        portfolio.user.save()

        Transaction.objects.create(
            portfolio=portfolio,
            stock=stock,
            transaction_type='buy',
            quantity=quantity,
            price_per_share=stock.current_price,
            total_price = quantity*stock.current_price,
        )

        return JsonResponse({'status': 'Stock purchased successfully!'})

    return JsonResponse({'status': 'Invalid request'}, status=400)


@login_required(login_url='/login/')
@csrf_exempt
def add_to_watchlist(request):
    if request.method == 'POST':
        stock_id = request.POST.get('stock_id')
        stock = get_object_or_404(Stock, id=stock_id)


        if Watchlist.objects.filter(user=request.user, stock=stock).exists():
            return JsonResponse({'status': 'Stock is already in your watchlist.'}, status=400)

        watchlist_item = Watchlist.objects.create(user=request.user, stock=stock)
        return JsonResponse({'status': 'Stock added to watchlist!'})

    return JsonResponse({'status': 'Invalid request'}, status=400)

@login_required(login_url='/login/')
@csrf_exempt
def remove_from_watchlist(request):
    if request.method == 'POST':
        stock_id = request.POST.get('stock_id')
        stock = get_object_or_404(Stock, id=stock_id) 

        try:
            watchlist_item = Watchlist.objects.get(user=request.user, stock=stock)
            watchlist_item.delete() 
            return JsonResponse({'status': f'{stock.name} removed from your watchlist.'})
        except Watchlist.DoesNotExist:
            return JsonResponse({'status': f'{stock.name} is not in your watchlist.'})

    return JsonResponse({'status': 'Invalid request.'})



@login_required(login_url='/login/')
def sell_stock(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, portfolio__user=request.user)

    if transaction.transaction_type != 'buy' or transaction.quantity == 0:
        messages.error(request, 'No stocks to sell in this transaction.')
        return redirect('home') 

    stock = transaction.stock

    total_amount_obtained = transaction.quantity * stock.current_price

    user = request.user
    user.budget += total_amount_obtained
    user.save()

    stock.quantity += transaction.quantity
    stock.save()
    new_transaction = Transaction(
        portfolio = transaction.portfolio,
        stock = transaction.stock,
        transaction_type = 'sell',
        quantity = transaction.quantity,
        price_per_share = stock.current_price,
        total_price = transaction.quantity*stock.current_price,

    )
    transaction.transaction_type = 'bs'
    transaction.transaction_date = timezone.now() - timedelta(seconds=1)
    transaction.save()


    new_transaction.save()

    messages.success(request, f'Successfully sold stocks for Rs. {total_amount_obtained:.2f}.')

    return redirect(f'/?sold=True&amount={total_amount_obtained:.2f}')

@login_required(login_url='/login/')
def update_graph(request, portfolio_id):
    portfolio = Portfolio.objects.get(portfolio_id=portfolio_id)
    make_graph(portfolio) 

    graph_url = portfolio.graphs.url 
    return JsonResponse({'graph_url': graph_url})

@login_required(login_url='/login/')
def success_page(request):

    latest_payment = Payment.objects.filter(user=request.user).order_by('-timestamp').first()

    if latest_payment and latest_payment.success:
        transaction_id = latest_payment.stripe_charge_id
        amount = latest_payment.amount
        date = latest_payment.timestamp.strftime('%Y-%m-%d %H:%M:%S') 
    else:
        transaction_id = "N/A"
        amount = 0.00
        date = "N/A"

    return render(request, 'stock/success_page.html', {
        'transaction_id': transaction_id,
        'amount': amount,
        'date': date,
    })


def payment_view(request):
    if request.method == "POST":
        token = request.POST.get("stripeToken")
        amount = int(float(request.POST.get("amount")) * 100) 

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="inr", 
                source=token,
                description="Payment Description",
            )

            payment = Payment.objects.create(
                user=request.user,
                amount=amount / 100,  
                stripe_charge_id=charge.id,
                success=True
            )

            user = User.objects.get(user=request.user)  
            user.budget += payment.amount  
            user.save()  

            messages.success(request, "Payment Successful! Your budget has been updated.")
            return redirect("success_page")

        except stripe.error.CardError as e:
            messages.error(request, f"Your card was declined: {e.error.message}")
            return redirect("payment_view")

    return render(request, "stock/payment_form.html", {"stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY})

def stock_analysis(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    
    # Fetch last 20 days data
    actual_data = fetch_stock_data(stock.id)
    if actual_data is None:
        return JsonResponse({"status": "Error fetching stock data."})
    
    context = {
        'stock': stock,
    }
    return render(request, 'stock/stock_analysis.html', context)
