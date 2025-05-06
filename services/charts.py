import pandas as pd
from datetime import date
from typing import List, Dict, Any

from services.dataset import PricesCache


def generate_chart_data(
    stocks: List[Dict[str, float]],
    tickers_info: Dict[str, Any],
    end_date: date
) -> Dict[str, Any]:
    """
    Build chart data for a given portfolio allocation up to end_date.
    stocks: list of { 'ticker': str, 'weight': float }
    tickers_info: dict of ticker metadata (must include 'sector').
    """
    tickers = [s["ticker"] for s in stocks]
    prices = PricesCache.get_prices()
    prices = prices[prices["ticker"].isin(tickers)]
    prices = prices[prices["date"] <= pd.to_datetime(end_date)]
    most_recent_ipo_date = prices.sort_values(["ticker", "date"]).groupby("ticker").head(1)['date'].max()
    prices = prices[prices["date"] >= most_recent_ipo_date]

    price_df = (
        prices[prices["ticker"].isin(tickers)]
        .pivot(index="date", columns="ticker", values="price")
        .sort_index()
    )
    if price_df.empty:
        raise ValueError("No price data available for given tickers and date range.")

    weights = {s["ticker"]: s["weight"] for s in stocks}
    norm = price_df.div(price_df.iloc[0])
    equity_series = norm.mul(pd.Series(weights)).sum(axis=1)
    dates = [d.strftime("%Y-%m-%d") for d in equity_series.index]
    equity = equity_series.tolist()

    cummax = equity_series.cummax()
    drawdown = (equity_series / cummax - 1).tolist()

    sector_map: Dict[str, float] = {}
    for ticker, w in weights.items():
        sector = tickers_info.get(ticker, {}).get("sector", "Unknown")
        sector_map[sector] = sector_map.get(sector, 0.0) + w
    sector_labels = list(sector_map.keys())
    sector_weights = list(sector_map.values())

    returns = price_df.pct_change().dropna(how="all")
    corr_df = returns.corr().fillna(0)
    corr_matrix = corr_df.reindex(index=tickers, columns=tickers).values
    heatmap_data_points = []
    for i, row_ticker in enumerate(tickers):
        for j, col_ticker in enumerate(tickers):
            if i < corr_matrix.shape[0] and j < corr_matrix.shape[1]:
                heatmap_data_points.append({"x": j, "y": i, "v": float(corr_matrix[i, j])})
            else:
                heatmap_data_points.append({"x": j, "y": i, "v": 0.0})

    return {
        "dates": dates,
        "equity": equity,
        "drawdown": drawdown,
        "sector_labels": sector_labels,
        "sector_weights": sector_weights,
        "tickers": tickers,
        "heatmap_data_points": heatmap_data_points
    }