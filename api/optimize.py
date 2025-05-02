from typing import Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

import pandas as pd
from services.dataset import PricesCache
from services.registry import ModelRegistry
from skfolio.preprocessing import prices_to_returns


class OptimizeRequest(BaseModel):
    model: str
    risk_model: str
    capital: float


class OptimizeResponse(BaseModel):
    weights: Dict[str, float]


router = APIRouter()

@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(req: OptimizeRequest):
    # load ML picker
    picker = ModelRegistry.get_picker(req.model)
    if picker is None:
        raise HTTPException(status_code=404, detail="Unknown model")

    # load risk function
    risk_fn = ModelRegistry.get_risk_fn(req.risk_model)
    if risk_fn is None:
        raise HTTPException(status_code=404, detail="Unknown risk model")

    # load full dataset
    df = PricesCache.get_prices()

    def sync_opt():
        # 1) select feature columns and predict probabilities
        feature_cols = [c for c in df.columns if c not in [
            "ticker", "date", "quarter_id", "close_raw", "outperformed"
        ]]
        X = df[feature_cols].values
        df["pred_proba"] = picker.predict_proba(X)[:, 1]

        # 2) select latest quarter per ticker and average probability
        latest_q = df.groupby("ticker")["quarter_id"].max().reset_index()
        data_latest = pd.merge(df, latest_q, on=["ticker", "quarter_id"])
        avg_pred = data_latest.groupby("ticker")["pred_proba"].mean().reset_index()
        selected = avg_pred[avg_pred["pred_proba"] > 0.5]["ticker"].tolist()
        if not selected:
            raise HTTPException(status_code=422, detail="No tickers selected by model")

        # 3) build price matrix from close_raw
        price = (
            df[df["ticker"].isin(selected)]
            .pivot(index="date", columns="ticker", values="close_raw")
            .sort_index()
        )

        # 4) compute returns
        returns = prices_to_returns(price)

        # 5) compute weights via chosen risk function
        weights, _ = risk_fn(returns)
        return selected, weights

    # run optimization in threadpool to avoid blocking
    selected, weights = await run_in_threadpool(sync_opt)

    # scale weights by capital
    scaled = {ticker: float(w * req.capital) for ticker, w in zip(selected, weights)}
    return OptimizeResponse(weights=scaled)