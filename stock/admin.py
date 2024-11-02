from django.contrib import admin
from .models import Stock, User, Dividend, Watchlist, Transaction, Portfolio, Payment, UserSettings# Import your model here

# Register your model with the admin site
admin.site.register(Stock)
admin.site.register(User)
admin.site.register(Dividend)
admin.site.register(Watchlist)
admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(Payment)
admin.site.register(UserSettings)

