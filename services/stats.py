import pandas as pd
from skfolio.preprocessing import prices_to_returns


def load_benchmark_returns(path: str) -> pd.Series:
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'], format="%Y%m%d")
    df = df.set_index("date").sort_index()
    weekly_close = df["close"].resample("W-FRI").last()
    returns_df = prices_to_returns(weekly_close.to_frame("spy"))
    return returns_df["spy"]


def compute_stats(ptf) -> dict:
    return ptf.summary().to_dict()
