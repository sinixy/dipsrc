from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel
from typing import Dict, Optional, List
from uuid import uuid4
from datetime import datetime

from config import settings

class PortfolioObject(BaseModel):
    _id: Optional[str] = None
    name: Optional[str] = ''
    created_at: Optional[datetime] = None
    end_date: datetime
    capital: int
    stocks: list[Dict]
    model: str
    optimizer: str
    notes: Optional[str] = ''

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_portfolio(portfolio: PortfolioObject, request: Request):
    db = request.app.state.db
    data = portfolio.model_dump()
    if not data.get("created_at"):
        data["created_at"] = datetime.now()
    if not data.get('name'):
        data['name'] = f"Portfolio {data['created_at'].isoformat(timespec='seconds')}"
    new_id = uuid4().hex
    doc = {"_id": new_id, **data}
    await db[settings.PORTFOLIO_COLLECTION].insert_one(doc)
    return {'id': new_id, 'name': data['name'], 'created_at': data['created_at']}

@router.get("/", response_model=List[PortfolioObject])
async def list_portfolios(request: Request):
    db = request.app.state.db
    docs = await db[settings.PORTFOLIO_COLLECTION].find().to_list(length=None)
    return [
        PortfolioObject(
            id=doc["_id"],
            weights=doc["weights"],
            stats=doc["stats"],
            capital=doc["capital"],
            created_at=doc["created_at"]
        )
        for doc in docs
    ]

@router.get("/{portfolio_id}", response_model=PortfolioObject)
async def get_portfolio(portfolio_id: str, request: Request):
    db = request.app.state.db
    doc = await db[settings.PORTFOLIO_COLLECTION].find_one({"_id": portfolio_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioObject(
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
