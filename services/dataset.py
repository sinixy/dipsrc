import pandas as pd


class PricesCache:
    _df: pd.DataFrame = None

    @classmethod
    def load(cls, path: str):
        cls._df = pd.read_csv(path, parse_dates=["date"])

    @classmethod
    def get_prices(cls) -> pd.DataFrame:
        if cls._df is None:
            raise RuntimeError("PricesCache not initialized")
        return cls._df.copy()