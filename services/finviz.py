import os
import aiohttp
import pandas as pd
from io import StringIO

from config import settings

async def get_ticker_info(tickers: list[str]) -> pd.DataFrame:
    url = (
        f"https://elite.finviz.com/export.ashx?v=152&t={','.join(tickers)}"
        f"&o=-change&c=1,2,3,5,6,7,75,16,82,78,28,38,39,40,41,42,44,46,48,54,65,66&auth={settings.FINVIZ_API_KEY}"
    )
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        text = await resp.text()
    df = pd.read_csv(StringIO(text))
    df.columns = [col.lower() for col in df.columns]
    return df