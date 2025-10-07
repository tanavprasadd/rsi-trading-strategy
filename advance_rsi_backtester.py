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
data = yf.download('BA', start = '2020-01-01', end = '2025-10-01') # Date format is YYYY- MM - DD
data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
data.dropna(inplace=True)  # removes any missing data points which is important for calculations 

# Calculating RSI function 
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0,0)
    loss = -delta.where(delta < 0,0) # Since we're dealing with loss it has to be "-delta"
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100/(1+rs))
    return rsi
data['RSI'] = calculate_rsi(data['Close'])

# SMA filler (reduces false RSI signals)
data['SMA200'] = data['Close'].rolling(window=200).mean()
print(data.columns)
# Generating the trading signals
# Buying when the RSI < number and the price is above the SMA200
# Selling when the RSI > number and the price is below SMA200
data['Signal'] = 0
data.loc[(data['RSI'] < 45) & (data['Close'] > data['SMA200']), 'Signal'] = 1
data.loc[(data['RSI'] > 75) & (data['Close'] < data['SMA200']), 'Signal'] = -1

# Strategy returns 
data['Market Return'] = data['Close'].pct_change() # pct_chagne gives the daily market returns (today-yesterday)/yesterday
data['Strategy Return'] = data['Market Return'] * data['Signal'].shift(1) # Strategy Return = market return * yesterday's signal
# shift(1) means using yesterday's signal to avoid lookahead bias

data['Cumulative Market Return'] = (1 + data['Market Return']).cumprod() # the compounds return over time
data['Cumulative Strategy Return'] = (1 + data['Strategy Return']).cumprod()
# if daily returns are [0.01, -0.02, 0.03], cumulative return = (1+0.01)*(1-0.02)*(1+0.03)

transaction_cost = 0.001 # 0.1% transaction costs
# Calculate when trades occur 
data['Trade'] = data['Signal'].diff().abs() # This will be 2 when we buy or sell, 0 otherwise
#  Subtract the transaction cost from startegy reeturn for only when a trade happens 
data['Strategy Return Net'] = data['Strategy Return'] - data['Trade'] * transaction_cost
data['Cumulative Strategy Return Net'] = (1 + data['Strategy Return Net']).cumprod()

# Performance metrics
total_return_net = data['Cumulative Strategy Return Net'].iloc[-1] - 1
annualised_return_net = data['Strategy Return Net'].mean() * 252 # 252 is the number of trading days in a year
annualised_vol_net = data['Strategy Return Net'].std() * np.sqrt(252) # Annualised Volatility = daily return std × √252
sharpe_ratio_net = annualised_return_net / annualised_vol_net if annualised_vol_net != 0 else 0
max_drawdown_net = (data['Cumulative Strategy Return Net'].cummax() - data['Cumulative Strategy Return Net']).max() #the worst peak to trough ratio

print("Strategy performance metrics")
print(f"Total Return: {total_return_net:.2%}")
print(f"Annualised Return: {annualised_return_net:.2%}")
print(f"Annualised Volatility: {annualised_vol_net:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio_net:.2%}")
print(f"Max Drawdown: {max_drawdown_net:.2%}")

# Plotting 
plt.figure(figsize=(12,6))
plt.plot(data['Cumulative Market Return'], label='Market (Buy & Hold)', linestyle='--')
plt.plot(data['Cumulative Strategy Return'], label='RSI Strategy', color='green')
plt.plot(data['Cumulative Strategy Return Net'], label='RSI Strategy(Net Of Costs)', color='red')
plt.title('RSI Trading Strategy vs Market Performance')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend()
plt.grid()
plt.show()