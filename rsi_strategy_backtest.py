# Tanav Praasd
# This code produces a graph that shows  us how our RSI trading bot preformed compared to the overall market
# Blue line shows us what the result would've been if we bought and held on (Market Return)
# The orange line is the result of the bot using the RSI in deciding when to buy and stay out (Strategy Return)

# Import libraries 

import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

# Get real world data so we can calculate the RSI and build the strategy 
data = yf.download('AAPL', start = '2024-03-01', end = '2025-03-29')
print(data.head())

# Calculating the RSI
# This will tell us when the stock is over-bought or over-sold
def calculate_rsi(series, period = 14):
    delta = series.diff() # Calculates the difference between each closing price
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
data['RSI'] = calculate_rsi(data['Close'])

# Create buy and sell signals   
data['Signal'] = 0
data.loc[data['RSI'] < 30, 'Signal'] = 1
data.loc[data['RSI'] > 70, 'Signal'] = -1
data['Position'] = data['Signal'].diff()

# Calculating strategy return
data['Market Return'] = data['Close'].pct_change()
data['Strategy Return'] = data['Market Return'] * data['Position']

# Plot startegy vs market
(1 + data[['Market Return', 'Strategy Return']]).cumprod().plot(figsize=(12,6))
plt.title('Strategy Preformnace vs Market')
plt.xlabel('Date')
plt.ylabel('Cumlative Return')
plt.grid()
plt.show()
# Blue line shows us what will happen if we bought and held on 
# Orange line shows us what the result the bot used using the RSI