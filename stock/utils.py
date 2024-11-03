import requests
from django.conf import settings
import time
from django.utils import timezone
from .models import Stock, Dividend
from django.shortcuts import render, get_object_or_404, redirect
from celery import shared_task
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import numpy as np
from xgboost import XGBRegressor
import io
from django.core.files.base import ContentFile
import base64
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import logging
from django.db import transaction


logger = logging.getLogger(__name__)


API_KEY = 'csiinh9r01qt46e7uh9gcsiinh9r01qt46e7uha0'
BASE_URL = 'https://finnhub.io/api/v1/quote'

stock_symbols = [
    'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'META', 'BRK.B', 'JPM', 'V',
    'JNJ', 'UNH', 'PG', 'HD', 'DIS', 'PYPL', 'VZ', 'INTC', 'CMCSA', 'ADBE', 
    'NFLX', 'NKE', 'T', 'MRK', 'XOM', 'PEP', 'CSCO', 'KO', 'ABT', 'PFE', 
    'CVX', 'MDT', 'WMT', 'TMO', 'TXN', 'QCOM', 'COST', 'LLY', 'SBUX', 'NOW',
    'AMGN', 'INTU', 'ISRG', 'MDLZ', 'ATVI', 'SNAP', 'BKNG', 'GILD', 'SHOP', 
    'ZM', 'ADP', 'LRCX', 'NEM', 'SPGI', 'C', 'MS', 'USB', 'SCHW', 'F', 
    'GM', 'BA', 'CAT', 'HON', 'IBM', 'MMM', 'GS', 'MSFT', 'ORCL', 'CRM',
    'AIG', 'CVS', 'MCD', 'MO', 'BK', 'BMY', 'CL', 'COP', 'DD', 'DHR',
    'DUK', 'EMR', 'EXC', 'FDX', 'GE', 'GM', 'HAL', 'HUM', 'IBM', 'INTC',
    'LMT', 'LOW', 'MCO', 'MDLZ', 'MET', 'MMM', 'MS', 'NEE', 'NEE', 'NSC',
    'PEP', 'PNC', 'PYPL', 'RTX', 'SBUX', 'SO', 'SPGI', 'TGT', 'TMO', 'TXN'
]


@shared_task
def fetch_and_load_stock_data():
    for symbol in stock_symbols:
        try:
            # Fetch the current quote
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

            # Fetch the company profile to get the stock name
            profile_response = requests.get('https://finnhub.io/api/v1/stock/profile2', params={
                'symbol': symbol,
                'token': API_KEY
            })
            profile_data = profile_response.json()
            stock_name = profile_data.get('name', 'N/A')  # Default to 'N/A' if not found

            # Check if stock exists to maintain the quantity if present
            stock, created = Stock.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'name': stock_name,
                    'market': 'N/A',
                    'quantity': 100,
                    'current_price': current_price,
                    'open_price': open_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'previous_close': previous_close
                }
            )

            if not created:
                stock.current_price = current_price
                stock.open_price = open_price
                stock.high_price = high_price
                stock.low_price = low_price
                stock.previous_close = previous_close
                stock.save()

            Dividend.objects.update_or_create(
               stock = stock,
           )

                
            if created:
                print(f"Created new stock entry: {symbol}")
            else:
                print(f"Updated stock entry: {symbol}")
                
        except Exception as e:
            print(f"An error occurred for {symbol}: {e}")

@shared_task
def fetch_and_load_stocks_periodically(delay=60):
    while True:
        fetch_and_load_stock_data()
        time.sleep(delay)

# To start periodic fetching:
# fetch_and_load_stocks_periodically(delay=60)


@shared_task
def make_graph(portfolio):
    pnl_data = portfolio.get_pnl_data()

    sell_transactions = []
    cumulative_pnl_list = []
    sell_count = 0

    for entry in pnl_data:
        if entry['transaction_type'] == 'sell': 
            sell_transactions.append(f"Sell {sell_count + 1}")
            cumulative_pnl_list.append((entry['pnl']/entry['inv_pnl'])*100)
            sell_count += 1

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

@shared_task
def fetch_stock_data(stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    try:
        data = yf.download(stock.symbol, start=start_date, end=end_date, interval="1d")
        if data.empty:
            return {"status": "Error: No data found for the specified stock symbol."}
        actual_data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        graph_path = generate_stock_graph(stock.symbol, actual_data)
        stock.image = graph_path
        stock.save()
        return {"status": "Success", "data": actual_data}
    except Exception as e:
        return {"status": f"Error fetching stock data: {str(e)}"}
    
@shared_task
def generate_stock_graph(stock_symbol, actual_data):
    actual_data.reset_index(drop=True, inplace=True)

    x = actual_data[['Close']][1:-1]
    actual_data['target'] = actual_data['Close'].shift(-1)
    y = actual_data[['target']][1:-1]

    y = y.ffill()
    x = x.ffill()
    x = x[:len(y)]

    if len(x) == 0 or len(y) == 0:
        print("Not enough data to fit the model.")
        return None

    model = XGBRegressor(n_estimators=100, objective='reg:squarederror')
    model.fit(x, y)


    last_close = actual_data['Close'].values[-2][0]
    future_predictions = []


    for _ in range(5):
        next_pred = model.predict(np.array([[last_close]]))
        future_predictions.append(next_pred[0])
        last_close = next_pred[0]

    plt.figure(figsize=(12, 6))
    plt.plot(range(len(actual_data['Close'])), actual_data['Close'], color="blue", label="Last Closing Prices", marker='o')
    
    future_indices = range(len(actual_data['Close']), len(actual_data['Close'])+5)
    plt.plot(future_indices, future_predictions, color="red",  label="Predicted Next 5 Days Closing Price", marker='o')
    
    plt.xlabel("Index")
    plt.ylabel("Price")
    plt.legend()
    plt.title(f"{stock_symbol} - Closing Price Prediction for Next 5 Days")

    graph_path = os.path.join(settings.BASE_DIR, 'static', 'stock', 'stock_graph', f'{stock_symbol}.png')
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    plt.savefig(graph_path)
    plt.close()

    print(f"Graph saved at: {graph_path}")
    return graph_path
