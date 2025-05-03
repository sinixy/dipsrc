import aiohttp
import yfinance as yf


async def get_fear_and_greed() -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Safari/537.36"
        )
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata/") as resp:
            resp.raise_for_status()
            resp = await resp.json()
            return resp['fear_and_greed']

def get_vix_info() -> dict:
    ticker = yf.Ticker("^VIX")
    return ticker.info['previousClose']
