from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Stock, Portfolio, Transaction

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
    return render(request, 'stock/stocks.html')

def portfolio(request):
    return render(request, 'stock/portfolio.html')

def transactions(request):
    return render(request, 'stock/transactions.html')

