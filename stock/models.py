from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import timedelta


# Custom user manager
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


# User model
class User(AbstractBaseUser):
    ROLES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, default='defaultemail@example.com')
    username = models.CharField(max_length=50, unique=True, default='Trader')
    first_name = models.CharField(max_length=50, default='FirstName')
    last_name = models.CharField(max_length=50, default='LastName')
    phone = models.CharField(max_length=15, blank=True, default='000-000-0000')
    role = models.CharField(max_length=5, choices=ROLES, default='user')
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=5000.00)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='static/stock/profile_pictures/', default='static/stock/profile_pictures/profile.jpg')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True  # Simplify for now

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_superuser  # Adjust this logic as necessary
    


# Portfolio model
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    portfolio_id = models.BigAutoField(primary_key=True)
    portfolio_name = models.CharField(max_length=100, default='My Portfolio')
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    graphs = models.ImageField(upload_to='static/stock/graphs/', default='static/stock/graphs/graph.jpg')


    def __str__(self):
        return f"{self.portfolio_name} - {self.user.username}"
    
    def get_pnl_data(self):
        start_date = timezone.now() - timedelta(days=30)
        transactions = self.transaction_set.filter(transaction_date__gte=start_date)
        pnl = 0
        inv_pnl = 0
        pnl_data = []
        for transaction in transactions:
            if transaction.transaction_type == 'bs':
                pnl -= transaction.total_price  # Loss due to bought-then-sold
                inv_pnl += transaction.total_price
            elif transaction.transaction_type == 'sell':
                pnl += transaction.total_price  # Revenue from the sale
            pnl_entry = {
                'date': transaction.transaction_date.date(),
                'transaction_type': transaction.transaction_type,
                'pnl': pnl,
                'inv_pnl': inv_pnl,
            }

            pnl_data.append(pnl_entry)

        return pnl_data


# Stock model
from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True, default='SYMBL')
    name = models.CharField(max_length=100, default='Default Stock')
    market = models.CharField(max_length=50, default='Unknown Market')
    quantity = models.PositiveIntegerField(default=0)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    open_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    high_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    low_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    previous_close = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='static/stock/stock_graph/', default='static/stock/stock_graph/default.jpg')


    def __str__(self):
        return f"{self.symbol} - {self.name}"



# Transaction model
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('bs', 'bought_then_sold')
    ]
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, default=None)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, default=None)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES, default='buy')
    quantity = models.PositiveIntegerField(default=0)
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_date = models.DateTimeField(default=timezone.now)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f"{self.transaction_type} - {self.stock.name} - {self.quantity}"


# Watchlist model
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, default=None)
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'stock')

    def __str__(self):
        return f"{self.user.username} - {self.stock.name}"


# Dividend model
class Dividend(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, default=None)
    dividend_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payout_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Dividend for {self.stock.name}"


# UserSettings model
class UserSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    setting_name = models.CharField(max_length=100, default='Default Setting')
    setting_value = models.CharField(max_length=255, blank=True, null=True, default='Default Value')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.setting_name} - {self.user.username}"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment {self.id} by {self.user.username} - Success: {self.success}"