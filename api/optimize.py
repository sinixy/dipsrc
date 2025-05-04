from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from starlette.concurrency import run_in_threadpool

import pandas as pd

from services.dataset import PricesCache
from services.registry import ModelRegistry
from services.stats import compute_stats, compute_equity_curve, compute_sector_weights
from services.finviz import get_ticker_info
from skfolio.preprocessing import prices_to_returns


class OptimizeRequest(BaseModel):
    model: str
    risk_model: str
    end_date: date
    capital: float

class OptimizeResponse(BaseModel):
    allocation: Dict[str, Any]
    stats: Dict[str, str]
    equity_curve: Dict[str, list]
    sector_weights: dict[str, float]
    tickers: Dict[str, Any]

router = APIRouter()

def normalize_weights(weights: dict, prices: pd.Series, capital: float) -> list[dict[str, float]]:
    stocks = []
    w_sum = 0
    for t, w in weights.items():
        price = prices.get(t)
        if not price: continue
        shares = int(capital * w / price)
        if shares > 0:
            w_sum += w
            stocks.append({'ticker': t, 'price': price, 'weight': w})
    for s in stocks:
        weight = s['weight'] / w_sum
        shares = int(weight * capital / s['price'])
        allocated = shares * s['price']
        s['weight'] = weight
        s['allocated'] = allocated
        s['shares'] = shares
    return sorted(stocks, key=lambda x: x['weight'], reverse=True)

@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(req: OptimizeRequest):
    picker = ModelRegistry.get_picker(req.model)
    if picker is None:
        raise HTTPException(status_code=404, detail="Unknown model")

    risk_fn = ModelRegistry.get_risk_fn(req.risk_model)
    if risk_fn is None:
        raise HTTPException(status_code=404, detail="Unknown risk model")

    dataset, prices = PricesCache.get_dataset(), PricesCache.get_prices()
    dataset = dataset[dataset["date"] <= pd.to_datetime(req.end_date)]

    def sync_opt():
        feature_cols = [c for c in dataset.columns if c not in [
            "ticker", "date", "quarter_id", "close_raw", "outperformed"
        ]]
        X = dataset[feature_cols].values
        dataset["pred_proba"] = picker.predict_proba(X)[:, 1]

        latest_q = dataset.groupby("ticker")["quarter_id"].max().reset_index()
        data_latest = pd.merge(dataset, latest_q, on=["ticker", "quarter_id"])
        avg_pred = data_latest.groupby("ticker")["pred_proba"].mean().reset_index()
        selected = avg_pred[avg_pred["pred_proba"] > 0.5]["ticker"].tolist()
        if not selected:
            raise HTTPException(status_code=422, detail="No tickers selected by model")

        prices_selected = (
            prices[prices["ticker"].isin(selected)]
            .pivot(index="date", columns="ticker", values="price")
            .sort_index()
        )
        returns = prices_to_returns(prices_selected)
        weights, ptf = risk_fn(returns)
        return selected, weights, ptf

    selected, weights, ptf = await run_in_threadpool(sync_opt)

    weights = dict(zip(selected, weights))
    stats = compute_stats(ptf)
    equity_curve = compute_equity_curve(ptf)

    ticker_info = await get_ticker_info(selected)
    stocks = normalize_weights(weights, ticker_info.set_index('ticker')['price'], req.capital)
    total_capital = sum(s['allocated'] for s in stocks)
    
    sector_weights = compute_sector_weights(weights, ticker_info)

    return OptimizeResponse(
        allocation={'stocks': stocks, 'total_capital': total_capital, 'leftover_capital': req.capital - total_capital},
        stats=stats,
        equity_curve=equity_curve,
        tickers=ticker_info.set_index('ticker').to_dict("index"),
        sector_weights=sector_weights
    )