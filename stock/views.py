from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Stock, Portfolio, Transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import fetch_and_load_stock_data  # Import your function

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

def home(request):
    return render(request, 'stock/home.html')

def login(request):
    return render(request, 'stock/login.html')

def register(request):
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

