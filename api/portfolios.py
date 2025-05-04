from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any
from uuid import uuid4
from datetime import datetime, date
import pandas as pd

from services.optimization import optimize_portfolio, normalize_weights
from services.stats import compute_stats
from services.dataset import PricesCache
from services.registry import ModelRegistry
from services.reminders import create_reminders_for_portfolio
from services.finviz import get_ticker_info
from config import settings

class PortfolioObject(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = ''
    created_at: Optional[datetime] = None
    end_date: datetime
    capital: int
    allocation: dict
    model: str
    optimizer: str
    notes: Optional[str] = ''

class RebalanceRequest(BaseModel):
    risk_model: str
    capital: Optional[float] = None
    as_of: Optional[date] = None

class RebalanceResponse(BaseModel):
    allocation: dict[str, Any]
    stats: dict[str, str]

class UpdatePortfolioRequest(BaseModel):
    allocation: Dict[str, Any]
    capital: float
    end_date: datetime

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_portfolio(portfolio: PortfolioObject, request: Request):
    db = request.app.state.db
    data = portfolio.model_dump()
    if 'id' in data: del data['id']
    if not data.get("created_at"):
        data["created_at"] = datetime.now()
    if not data.get('name'):
        data['name'] = f"Portfolio {data['created_at'].isoformat(timespec='seconds')}"
    new_id = uuid4().hex
    doc = {"_id": new_id, **data}

    await db[settings.PORTFOLIO_COLLECTION].insert_one(doc)
    
    create_reminders_for_portfolio(
        portfolio_id=new_id,
        created_at=doc["created_at"]
    )

    return {'_id': new_id, 'name': data['name'], 'created_at': data['created_at']}

@router.get("/", response_model=List[PortfolioObject])
async def list_portfolios(request: Request):
    db = request.app.state.db
    docs = await db[settings.PORTFOLIO_COLLECTION].find().to_list(length=None)
    return [
        PortfolioObject(**doc)
        for doc in docs
    ]

@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str, request: Request):
    db = request.app.state.db
    doc = await db[settings.PORTFOLIO_COLLECTION].find_one({"_id": portfolio_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    tickers = await get_ticker_info([s["ticker"] for s in doc["allocation"]['stocks']])
    return {**doc, 'tickers': tickers.set_index('ticker').to_dict("index")}

@router.put("/{portfolio_id}", response_model=PortfolioObject)
async def update_portfolio(
    portfolio_id: str,
    payload: UpdatePortfolioRequest,
    request: Request
):
    db = request.app.state.db
    update_data = {
        "allocation": payload.allocation,
        "capital": payload.capital,
        "end_date": payload.end_date
    }
    result = await db[settings.PORTFOLIO_COLLECTION].update_one(
        {"_id": portfolio_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    doc = await db[settings.PORTFOLIO_COLLECTION].find_one({"_id": portfolio_id})
    return PortfolioObject(**doc)

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(portfolio_id: str, request: Request):
    db = request.app.state.db
    res = await db[settings.PORTFOLIO_COLLECTION].delete_one({"_id": portfolio_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{portfolio_id}/rebalance", response_model=RebalanceResponse)
async def rebalance_portfolio(
    portfolio_id: str,
    body: RebalanceRequest,
    request: Request
):
    db = request.app.state.db
    doc = await db[settings.PORTFOLIO_COLLECTION].find_one({"_id": portfolio_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    stored_weights = {s["ticker"]: s["weight"] for s in doc['allocation']["stocks"]}
    selected = list(stored_weights.keys())

    capital = body.capital if body.capital else doc["capital"]
    as_of = pd.to_datetime(body.as_of) if body.as_of else datetime.now()

    prices = PricesCache.get_prices()
    prices = prices[(prices['ticker'].isin(selected)) & (prices["date"] <= as_of)]

    risk_fn = ModelRegistry.get_risk_fn(body.risk_model)
    if not risk_fn:
        raise HTTPException(status_code=404, detail="Unknown risk model")

    weights, ptf = optimize_portfolio(prices, selected, risk_fn)

    last_prices = (
        prices.sort_values(["ticker","date"])
        .groupby("ticker").tail(1)
        .set_index("ticker")['price']
    )
    stocks = normalize_weights(weights, last_prices, capital)
    total_capital = sum(s['allocated'] for s in stocks)

    stats = compute_stats(ptf)

    return RebalanceResponse(
        allocation={'stocks': stocks, 'total_capital': total_capital, 'leftover_capital': capital - total_capital},
        stats=stats
    )
