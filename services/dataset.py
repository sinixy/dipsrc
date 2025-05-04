import sqlite3
import pandas as pd

from config import settings

class PricesCache:
    _prices: pd.DataFrame = None
    _dataset: pd.DataFrame = None

    @classmethod
    def load(cls):
        # read prices directly from the SQLite 'prices' table
        con = sqlite3.connect(settings.DB_PATH)
        prices = pd.read_sql(
            "SELECT date, ticker, close as price FROM prices",
            con,
            parse_dates=["date"]
        )
        dataset = pd.read_sql(
            "SELECT * FROM dataset",
            con,
            parse_dates=["date"]
        )
        con.close()

        # drop excluded tickers
        prices = prices[~prices["ticker"].isin(settings.EXCLUDED_TICKERS)]
        dataset = dataset[~dataset["ticker"].isin(settings.EXCLUDED_TICKERS)]

        # store a copy in memory
        cls._prices = prices.sort_values(["ticker","date"]).reset_index(drop=True)
        cls._dataset = dataset.sort_values(["ticker","date"]).reset_index(drop=True)

    @classmethod
    def get_prices(cls) -> pd.DataFrame:
        if cls._prices is None:
            raise RuntimeError("PricesCache not initialized")
        return cls._prices.copy()
    
    @classmethod
    def get_dataset(cls) -> pd.DataFrame:
        if cls._dataset is None:
            raise RuntimeError("PricesCache not initialized")
        return cls._dataset.copy()
