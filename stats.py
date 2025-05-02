import aiohttp
import pandas as pd
from io import StringIO

from config import FINVIZ_API_KEY


async def get_stats(tickers: list[str]):
    async with aiohttp.ClientSession() as session:
        data = await session.get(
            f'https://elite.finviz.com/export.ashx?v=152&t={",".join(tickers)}&o=-change&c=1,2,3,5,6,7,75,16,82,78,28,38,39,40,41,42,44,46,48,54,65,66&auth={FINVIZ_API_KEY}'
        )
        df = pd.read_csv(
            StringIO(await data.text())
        ).set_index('Ticker')
        return df.to_dict('index')

def get_performance(dataset: pd.DataFrame, weights: dict):
    returns = dataset[weights.keys()].pct_change()
    portfolio_returns = returns.dot(pd.Series(weights))
    return ((1 + portfolio_returns).cumprod() * 100).dropna()

