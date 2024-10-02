from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('stocks/', views.stocks, name='stocks'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('transactions/', views.transactions, name='transactions'),

]
