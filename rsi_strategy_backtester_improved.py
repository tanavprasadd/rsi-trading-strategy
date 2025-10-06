# Tanav Prasad
# RSI Trading Strategy vs Market Benchmark
# This script is an improved version that calculates RSI-based buy/sell signals and compares strategy performance
# against a buy-and-hold benchmark using real stock data.

import pandas as pd
import yfinance as yf
import numpy as np 
import matplotlib.pyplot as plt

# This just makes our graph a little more modern and better looking
plt.style.use('seaborn-v0_8')

# Download our data
data = yf.download('AAPL', start = '2024-03-01', end = '2025-03-01')
data.dropna(inplace=True) #removes any missing data points which is important for calculations 

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

# Generate trading signals 
data['Signal'] = 0
data.loc[data['RSI'] < 30, 'Signal'] = 1 #Buy signal
data.loc[data['RSI'] > 70, 'Signal'] = -1 #Sell signal
# The issue I have right now is, this is too simple and not realistic 

# Calculate returns 
data['Market Return'] = data['Close'].pct_change() # pct_chagne gives the daily market returns (today-yesterday)/yesterday
data['Strategy Return'] = data['Market Return'] * data['Signal'].shift(1) # Strategy Return = market return * yesterday's signal
# shift(1) means using yesterday's signal to avoid lookahead bias

data['Cumulative Market Return'] = (1 + data['Market Return']).cumprod() # the compounds return over time
data['Cumulative Strategy Return'] = (1 + data['Strategy Return']).cumprod()
# if daily returns are [0.01, -0.02, 0.03], cumulative return = (1+0.01)*(1-0.02)*(1+0.03)

# Preformace metrics
total_return = data['Cumulative Strategy Return'].iloc[-1] - 1
annualised_return = data['Strategy Return'].mean() * 252 # 252 is the number of trading days in a year
annualised_vol = data['Strategy Return'].std() * np.sqrt(252) # Annualised Volatility = daily return std × √252
sharpe_ratio = annualised_return / annualised_vol if annualised_vol != 0 else 0
max_drawdown = (data['Cumulative Strategy Return'].cummax() - data['Cumulative Strategy Return']).max() #the worst peak to trough ratio

print("Strategy preformance metrics")
print(f"Total Return: {total_return:.2%}")
print(f"Annualised Return: {annualised_return:.2%}")
print(f"Annualised Volatility: {annualised_vol:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2%}")
print(f"Max Drawdown: {max_drawdown:.2%}")

# Plotting 
plt.figure(figsize=(12,6))
plt.plot(data['Cumulative Market Return'], label='Market (Buy & Hold)', linestyle='--')
plt.plot(data['Cumulative Strategy Return'], label='RSI Strategy', color='green')
plt.title('RSI Trading Strategy vs Market Performance')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend()
plt.grid()
plt.show() 