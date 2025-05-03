import pandas as pd

from config import settings


class PricesCache:
    _df: pd.DataFrame = None

    @classmethod
    def load(cls, path: str):
        df = pd.read_csv(path, parse_dates=["date"])
        cls._df = df.drop(df[df['ticker'].isin(settings.EXCLUDED_TICKERS)].index)

    @classmethod
    def get_prices(cls) -> pd.DataFrame:
        if cls._df is None:
            raise RuntimeError("PricesCache not initialized")
        return cls._df.copy()