from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

import pandas as pd

from config import settings
from services.dataset import PricesCache
from services.registry import ModelRegistry
from services.stats import load_benchmark_returns, compute_stats
from services.finviz import get_ticker_info
from skfolio.preprocessing import prices_to_returns


class OptimizeRequest(BaseModel):
    model: str
    risk_model: str

class OptimizeResponse(BaseModel):
    weights: Dict[str, float]
    stats: Dict[str, str]
    equity_curve: Dict[str, list]
    sector_weights: dict[str, float]
    tickers: Dict[str, Any]

router = APIRouter()

@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(req: OptimizeRequest):
    picker = ModelRegistry.get_picker(req.model)
    if picker is None:
        raise HTTPException(status_code=404, detail="Unknown model")

    risk_fn = ModelRegistry.get_risk_fn(req.risk_model)
    if risk_fn is None:
        raise HTTPException(status_code=404, detail="Unknown risk model")

    df = PricesCache.get_prices()

    def sync_opt():
        feature_cols = [c for c in df.columns if c not in [
            "ticker", "date", "quarter_id", "close_raw", "outperformed"
        ]]
        X = df[feature_cols].values
        df["pred_proba"] = picker.predict_proba(X)[:, 1]

        latest_q = df.groupby("ticker")["quarter_id"].max().reset_index()
        data_latest = pd.merge(df, latest_q, on=["ticker", "quarter_id"])
        avg_pred = data_latest.groupby("ticker")["pred_proba"].mean().reset_index()
        selected = avg_pred[avg_pred["pred_proba"] > 0.5]["ticker"].tolist()
        if not selected:
            raise HTTPException(status_code=422, detail="No tickers selected by model")

        price = (
            df[df["ticker"].isin(selected)]
            .pivot(index="date", columns="ticker", values="close_raw")
            .sort_index()
        )
        returns = prices_to_returns(price)
        weights, ptf = risk_fn(returns)
        return selected, weights, ptf

    selected, weights, ptf = await run_in_threadpool(sync_opt)

    weights = dict(zip(selected, weights))
    stats = compute_stats(ptf)

    curve = ptf.cumulative_returns_df
    eq_dates = [d.strftime("%Y-%m-%d") for d in curve.index]
    eq_values = curve.values.tolist()
    equity_curve = {"dates": eq_dates, "values": eq_values}

    ticker_info = await get_ticker_info(selected)
    w_df = (
        pd.DataFrame.from_dict(weights, orient='index', columns=['weight'])
        .reset_index()
        .rename(columns={'index': 'ticker'})
    )
    merged = w_df.merge(ticker_info[['ticker', 'sector']], on='ticker', how='left')
    sector_weights = merged.groupby('sector')['weight'].sum().to_dict()

    return OptimizeResponse(
        weights=weights,
        stats=stats,
        equity_curve=equity_curve,
        tickers=ticker_info.set_index('ticker').to_dict("index"),
        sector_weights=sector_weights
    )