import yfinance
import pandas as pd
import sqlite3
import json


connection = sqlite3.connect('data/data.db')
symbols = []
with open('data/sp500.json') as file:
    symbols = json.load(file)

for symbol in symbols:
    df: pd.DataFrame = yfinance.download(symbol, start='2004-01-01', end='2024-01-01', interval='1wk')
    df['symbol'] = symbol
    df = df[['symbol', 'Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
    df.columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
    df.to_sql('PRICES', connection, if_exists='append', index=False)