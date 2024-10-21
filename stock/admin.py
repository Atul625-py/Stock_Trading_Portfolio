from django.contrib import admin
from .models import Stock, User  # Import your model here

# Register your model with the admin site
admin.site.register(Stock)
admin.site.register(User)
