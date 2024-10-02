from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
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

