from django.db import models
from django.utils import timezone
import requests


class User(models.Model):
    ROLES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, default=' ')
    role = models.CharField(max_length=5, choices=ROLES, default='user')
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=5000)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(default='./static/stock/images/profile.jpg')

    def __str__(self):
        return self.username


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    portfolio_name = models.CharField(max_length=100, default='My Portfolio')
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.portfolio_name} - {self.user.username}"


class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    market = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.transaction_type} - {self.stock.name} - {self.quantity}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'stock')

    def __str__(self):
        return f"{self.user.username} - {self.stock.name}"


class Dividend(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    dividend_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout_date = models.DateField()

    def __str__(self):
        return f"Dividend for {self.stock.name}"


class UserSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    setting_name = models.CharField(max_length=100)
    setting_value = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.setting_name} - {self.user.username}"
