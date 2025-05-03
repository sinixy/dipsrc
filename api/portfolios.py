# api/portfolios.py
from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel
from typing import Dict, Optional, List
from uuid import uuid4
from datetime import datetime

from config import settings

class PortfolioIn(BaseModel):
    weights: Dict[str, float]
    stats: Dict[str, float]
    capital: float
    created_at: Optional[datetime] = None  # auto-set if missing

class PortfolioOut(BaseModel):
    id: str
    weights: Dict[str, float]
    stats: Dict[str, float]
    capital: float
    created_at: datetime

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

@router.post("/", response_model=PortfolioOut, status_code=status.HTTP_201_CREATED)
async def create_portfolio(portfolio: PortfolioIn, request: Request):
    db = request.app.state.db
    data = portfolio.dict()
    if not data.get("created_at"):
        data["created_at"] = datetime.now()
    new_id = uuid4().hex
    doc = {"_id": new_id, **data}
    await db[settings.PORTFOLIO_COLLECTION].insert_one(doc)
    return PortfolioOut(id=new_id, **data)

@router.get("/", response_model=List[PortfolioOut])
async def list_portfolios(request: Request):
    db = request.app.state.db
    docs = await db[settings.PORTFOLIO_COLLECTION].find().to_list(length=None)
    return [
        PortfolioOut(
            id=doc["_id"],
            weights=doc["weights"],
            stats=doc["stats"],
            capital=doc["capital"],
            created_at=doc["created_at"]
        )
        for doc in docs
    ]

@router.get("/{portfolio_id}", response_model=PortfolioOut)
async def get_portfolio(portfolio_id: str, request: Request):
    db = request.app.state.db
    doc = await db[settings.PORTFOLIO_COLLECTION].find_one({"_id": portfolio_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioOut(
        id=doc["_id"],
        weights=doc["weights"],
        stats=doc["stats"],
        capital=doc["capital"],
        created_at=doc["created_at"]
    )

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(portfolio_id: str, request: Request):
    db = request.app.state.db
    res = await db[settings.PORTFOLIO_COLLECTION].delete_one({"_id": portfolio_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
