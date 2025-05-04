import sqlite3
import pandas as pd
from datetime import datetime, timedelta

from config import settings
from model.price import download_prices
from model.features import resample_weekly, generate_technicals, normalize_features

DB = settings.DB_PATH  # e.g. "data/data.db"

def update_prices():
    con = sqlite3.connect(DB)
    # 1) get last updated datetime for 'prices'
    last = pd.read_sql(
        "SELECT datetime FROM last_updated WHERE data='prices'", con,
        parse_dates=["datetime"]
    )["datetime"].iloc[0]
    if last > (datetime.now() - timedelta(days=6)): return 0
    print('Updating prices...')

    start = (last + timedelta(days=1)).date().isoformat()

    # 2) load existing tables
    prices_old = pd.read_sql("SELECT * FROM prices", con, parse_dates=["date"])
    spy_old    = pd.read_sql("SELECT * FROM spy", con, parse_dates=["date"])

    # 3) download new data
    tickers = prices_old["ticker"].unique().tolist()
    new_prices = download_prices(tickers, start=start)
    new_spy = download_prices(["SPY"], start=start)

    # 4) concat, dedupe, sort, reset
    prices = pd.concat([prices_old, new_prices], ignore_index=True)
    prices = prices.drop_duplicates(subset=["ticker","date"])
    prices = prices.sort_values(["ticker","date"]).reset_index(drop=True)

    spy = pd.concat([spy_old, new_spy], ignore_index=True)
    spy = spy.drop_duplicates(subset=["date"])
    spy = spy.sort_values("date").reset_index(drop=True)

    # 5) replace tables
    prices.to_sql("prices", con, if_exists="replace", index=False)
    spy[['date','open','high','low','close','volume']].to_sql(
        "spy", con, if_exists="replace", index=False
    )

    # 6) bump last_updated
    now = datetime.now().isoformat()
    con.execute(
        "UPDATE last_updated SET datetime = ? WHERE data = 'prices'",
        (now,)
    )
    con.commit()
    con.close()

    return 1

def rebuild_dataset():
    print('Rebuilding dataset...')
    con = sqlite3.connect(DB)
    prices = pd.read_sql("SELECT * FROM prices", con, parse_dates=["date"])
    prices_w = resample_weekly(prices[["ticker","date","close","volume"]])
    spy = pd.read_sql("SELECT * FROM spy", con, parse_dates=["date"])
    spy = spy.assign(ticker="SPY")
    spy_w = resample_weekly(spy[["ticker","date","close","volume"]])

    tech = generate_technicals(prices_w, benchmark_df=spy_w[["date","close"]])
    tech = normalize_features(tech)

    ds = pd.read_sql("SELECT * FROM dataset", con, parse_dates=["date"])
    tech_cols = [c for c in tech.columns if c not in ("ticker","date")]
    fund = ds.drop(columns=tech_cols, errors="ignore")
    print(fund[fund['ticker'] == 'AAPL']['outperformed'].values)

    frames = []
    for tkr, t_df in tech.groupby("ticker"):
        f_df = fund[fund["ticker"]==tkr].sort_values("date")
        merged = pd.merge_asof(
            t_df.sort_values("date"),
            f_df,
            on="date",
            by="ticker",
            direction="backward"
        )
        frames.append(merged)

    new_ds = pd.concat(frames, ignore_index=True)
    new_ds = new_ds.sort_values(["ticker","date"]).reset_index(drop=True)

    no_fill = {"ticker","date","quarter_id","since_quarter_start","outperformed"}
    to_ffill = [c for c in fund.columns if c not in no_fill]
    new_ds[to_ffill] = new_ds.groupby("ticker")[to_ffill].ffill()

    # 5) overwrite
    new_ds.to_sql("dataset", con, if_exists="replace", index=False)
    con.close()

def run_full_update():
    update_prices()


if __name__ == "__main__":
    run_full_update()