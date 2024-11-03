from django.urls import path
from . import views
from .decorators import user_required, admin_required

urlpatterns = [
    path('', user_required(views.home), name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', user_required(views.profile), name='profile'),
    path('watchlist/', user_required(views.watchlist), name='watchlist'),
    path('stocks/', views.stocks, name='stocks'),  # Both groups can access
    path('portfolio/', user_required(views.portfolio), name='portfolio'),
    path('transactions/', views.transactions, name='transactions'),
    path('reload-stocks/',views.reload_stocks, name='reload_stocks'),
    path('logout/', views.user_logout, name='logout'),
    path('purchase_stock/', user_required(views.purchase_stock), name='purchase_stock'),
    path('add_to_watchlist/', user_required(views.add_to_watchlist), name='add_to_watchlist'),
    path('remove_from_watchlist/', user_required(views.remove_from_watchlist), name='remove_from_watchlist'),
    path('sell/<int:transaction_id>/', views.sell_stock, name='sell-stock'),
    path('update-graph/<int:portfolio_id>/', views.update_graph, name='update_graph'),
    path("payment/", views.payment_view, name="payment_view"),
    path("success/", views.success_page, name="success_page"),
    path('stock/<int:stock_id>/', views.stock_analysis, name='stock_analysis'),  
]
