# Tanav Prasad
# This is an improvement on my previous backtester using a more real-world rsi strategy 

# Import libraries 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# This just makes our graph a little more modern and better looking
plt.style.use('seaborn-v0_8')

# Get trading data 
data = yf.download('LMT', start = '2020-01-01', end = '2025-10-01') # Date format is YYYY- MM - DD
data.dropna(inplace=True)  # removes any missing data points which is important for calculations 

# Calculating RSI function 
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0,0)
    loss = delta.where(delta < 0,0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100/(1+rs))
    return rsi
data['RSI'] = calculate_rsi(data['Close'])