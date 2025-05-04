from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from starlette.concurrency import run_in_threadpool
import pandas as pd

from services.dataset import PricesCache
from services.registry import ModelRegistry
from services.stats import compute_stats, compute_equity_curve, compute_sector_weights
from services.finviz import get_ticker_info
from services.optimization import select_tickers, optimize_portfolio, normalize_weights


class OptimizeRequest(BaseModel):
    model: str
    risk_model: str
    end_date: date
    capital: float

class OptimizeResponse(BaseModel):
    allocation: dict[str, Any]
    stats: dict[str, str]
    equity_curve: dict[str, list]
    sector_weights: dict[str, float]
    tickers: dict[str, Any]

router = APIRouter()


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(req: OptimizeRequest):
    picker = ModelRegistry.get_picker(req.model)
    if picker is None:
        raise HTTPException(status_code=404, detail="Unknown model")

    risk_fn = ModelRegistry.get_risk_fn(req.risk_model)
    if risk_fn is None:
        raise HTTPException(status_code=404, detail="Unknown risk model")

    dataset, prices = PricesCache.get_dataset(), PricesCache.get_prices()
    cutoff = pd.to_datetime(req.end_date)
    dataset = dataset[dataset["date"] <= cutoff]
    # prices = prices[prices["date"]  <= cutoff]

    def opt():
        selected = select_tickers(dataset, picker)
        if not selected:
            raise HTTPException(status_code=422, detail="No tickers selected by model")
        weights, ptf = optimize_portfolio(prices, selected, risk_fn)
        return weights, ptf

    weights, ptf = await run_in_threadpool(opt)

    stats = compute_stats(ptf)
    equity_curve = compute_equity_curve(ptf)

    ticker_info = await get_ticker_info(list(weights.keys()))
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