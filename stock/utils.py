import requests
from django.conf import settings
import time
from django.utils import timezone
from .models import Stock, Dividend
from celery import shared_task
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


API_KEY = 'csiinh9r01qt46e7uh9gcsiinh9r01qt46e7uha0'
BASE_URL = 'https://finnhub.io/api/v1/quote'

stock_symbols = [
    'IBM', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'FB', 'TSLA', 'BRK.B', 'NVDA', 'JPM',
    'V', 'JNJ', 'UNH', 'PG', 'HD', 'DIS', 'PYPL', 'VZ', 'INTC', 'CMCSA', 'ADBE',
    'NFLX', 'NKE', 'T', 'MRK', 'XOM', 'PEP', 'CSCO', 'KO', 'ABT', 'PFE', 'CVX',
    'MDT', 'WMT', 'TMO', 'TXN', 'QCOM', 'COST', 'LLY', 'SBUX', 'NOW', 'AMGN',
    'INTU', 'ISRG', 'MDLZ', 'ATVI', 'SNAP', 'BKNG', 'GILD', 'SHOP', 'ZM', 'ADP',
    'LRCX', 'NEM', 'SPGI', 'C', 'MS', 'USB', 'SCHW'
]

def fetch_and_load_stock_data():
    for symbol in stock_symbols:
        try:
            response = requests.get(BASE_URL, params={
                'symbol': symbol,
                'token': API_KEY
            })
            data = response.json()
            
            if 'c' not in data:
                print(f"Error fetching data for {symbol}: {data.get('error', 'Unknown error')}")
                continue

            current_price = data['c']
            open_price = data.get('o', 0)
            high_price = data.get('h', 0)
            low_price = data.get('l', 0)
            previous_close = data.get('pc', 0)

            stock, created = Stock.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': symbol,
                    'market': 'N/A',
                    'quantity': 100 ,
                    'current_price': current_price,
                    'open_price': open_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'previous_close': previous_close
                }
            )

            Dividend.objects.update_or_create(stock=stock)

            if created:
                print(f"Created new stock entry: {symbol}")
            else:
                print(f"Updated stock entry: {symbol}")
        except requests.RequestException as e:
            print(f"Request error for {symbol}: {e}")
        except Exception as e:
            print(f"An error occurred for {symbol}: {e}")

@shared_task
def fetch_and_load_stocks_periodically(delay=30):
    while True:
        fetch_and_load_stock_data()
        time.sleep(delay)

# To start periodic fetching:
# fetch_and_load_stocks_periodically(delay=60)



def make_graph(portfolio):
    # Get transaction-wise PnL data
    pnl_data = portfolio.get_pnl_data()

    # Prepare data for each sell transaction
    sell_transactions = []
    cumulative_pnl_list = []
    sell_count = 0

    for entry in pnl_data:
        if entry['transaction_type'] == 'sell':  # Consider only 'sell' transactions
            sell_transactions.append(f"Sell {sell_count + 1}")
            cumulative_pnl_list.append((entry['pnl']/entry['inv_pnl'])*100)
            sell_count += 1

    # Plot the data
    plt.figure(figsize=(10, 5))
    plt.plot(sell_transactions, cumulative_pnl_list, marker='o')
    plt.title(f'Cumulative P&L per Sell Transaction for {portfolio.portfolio_name}')
    plt.xlabel('Sell Transactions')
    plt.ylabel('Cumulative Profit/Loss Percentages')
    plt.xticks(rotation=45)
    plt.grid()

    graph_path = os.path.join(settings.BASE_DIR, 'static/stock/graphs', f'{portfolio.portfolio_id}_pnl_graph.png')
    graph_dir = os.path.dirname(graph_path)
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
    plt.savefig(graph_path)
    plt.close()
    
    portfolio.graphs = graph_path
    portfolio.save()