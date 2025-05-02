import pandas as pd
import sqlite3
import os
import json
import requests
from tqdm import tqdm
from time import sleep
from datetime import datetime



def download_spy_components():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_df = tables[0]
    changes_df = tables[1]

    # Ensure directory exists
    os.makedirs("spy", exist_ok=True)

    # Save current snapshot as a JSON list of tickers
    snapshot = sp500_df['Symbol'].tolist()
    with open("spy/2025-04-20-snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    # Build a normalized change list
    records = []
    for idx, row in changes_df.iterrows():
        date = pd.to_datetime(row['Date']['Date']).strftime("%Y-%m-%d")
        if pd.notna(row['Added']['Ticker']):
            records.append({"date": date, "event": "add", "ticker": row['Added']['Ticker']})
        if pd.notna(row['Removed']['Ticker']):
            records.append({"date": date, "event": "remove", "ticker": row['Removed']['Ticker']})

    # Save component changes
    with open("spy/changes.json", "w") as f:
        json.dump(records, f, indent=2)

    print("Saved current snapshot and component changes.")


def get_sp500_snapshot(dt, latest_snapshot, change_events, latest_snapshot_date="2025-04-20"):
    """
    Reconstructs S&P500 index membership at a past date by rewinding the latest snapshot
    using all events that occurred after that date.

    Params:
    - dt: date to reconstruct snapshot for (e.g. "2025-03-01")
    - latest_snapshot: list or set of tickers as of latest_snapshot_date (default: "2025-04-20")
    - change_events: list of dicts with keys: date, event, ticker
    - latest_snapshot_date: known snapshot date that latest_snapshot represents

    Returns:
    - Set of tickers that were in the index on dt
    """
    snapshot = set(latest_snapshot)
    dt = datetime.strptime(dt, "%Y-%m-%d")
    latest_snapshot_date = datetime.strptime(latest_snapshot_date, "%Y-%m-%d")

    if dt > latest_snapshot_date:
        raise ValueError("Can't move forward in time from a snapshot in the future.")
    
    for event in sorted(change_events, key=lambda x: x["date"], reverse=True):
        event_date = datetime.strptime(event["date"], "%Y-%m-%d")

        if event_date > dt:
            if event["event"] == "add":
                snapshot.discard(event["ticker"])
            elif event["event"] == "remove":
                snapshot.add(event["ticker"])
        else:
            break

    return snapshot


def get_all_unique_tickers_since(dt: str, current_tickers: list, change_events: list) -> list:
    sn = get_sp500_snapshot(dt, current_tickers, change_events)
    return [{'ticker': ticker, 'name': ''} for ticker in sn.union(set(current_tickers))]


def load_prices(symbols, connection):
    '''
    stock data columns:
    <TICKER>,<PER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>,<OPENINT>
    AA.US,D,19700102,000000,2.27537,2.29565,2.27537,2.27537,26690.902166928,0
    
    database columns:
    CREATE TABLE "prices" (
        "date"	TIMESTAMP,
        "ticker"	TEXT,
        "open"	REAL,
        "high"	REAL,
        "low"	REAL,
        "close"	REAL,
        "volume"	INTEGER
    );
    '''
    for symbol in tqdm(symbols):
        filepath = f'data/stocks/{symbol.lower()}.us.txt'
        
        try:
            df = pd.read_csv(filepath)
        except:
            print(symbol, 'not found')
            continue

        df.drop(columns=['<PER>', '<TIME>', '<OPENINT>'], inplace=True)
        df.rename(columns={'<TICKER>': 'ticker', '<DATE>': 'date', '<OPEN>': 'open', '<HIGH>': 'high', '<LOW>': 'low', '<CLOSE>': 'close', '<VOL>': 'volume'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df['ticker'] = symbol
        df.to_sql('prices', connection, if_exists='append', index=False)

if __name__ == '__main__':
    pass