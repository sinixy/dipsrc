import pandas as pd
from skfolio import Portfolio
from skfolio.preprocessing import prices_to_returns


def load_benchmark_returns(path: str) -> pd.Series:
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'], format="%Y%m%d")
    df = df.set_index("date").sort_index()
    weekly_close = df["close"].resample("W-FRI").last()
    returns_df = prices_to_returns(weekly_close.to_frame("spy"))
    return returns_df["spy"]


def compute_stats(ptf: Portfolio) -> dict:
    return ptf.summary().to_dict()


def compute_equity_curve(ptf: Portfolio) -> dict:
    curve = ptf.cumulative_returns_df
    eq_dates = [d.strftime("%Y-%m-%d") for d in curve.index]
    eq_values = curve.values.tolist()
    return {"dates": eq_dates, "values": eq_values}

def compute_sector_weights(weights: dict, ticker_info: pd.DataFrame) -> dict:
    w_df = (
        pd.DataFrame.from_dict(weights, orient='index', columns=['weight'])
        .reset_index()
        .rename(columns={'index': 'ticker'})
    )
    merged = w_df.merge(ticker_info[['ticker', 'sector']], on='ticker', how='left')
    return merged.groupby('sector')['weight'].sum().to_dict()