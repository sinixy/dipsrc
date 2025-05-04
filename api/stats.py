from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date

from services.charts import generate_chart_data

router = APIRouter(prefix="/stats", tags=["stats"])


class ChartRequest(BaseModel):
    stocks: list[dict]
    tickers: Dict[str, Any]         # metadata per ticker (must include 'sector')
    end_date: date                  # cutoff date for price data


class ChartDataResponse(BaseModel):
    dates: List[str]
    equity: List[float]
    drawdown: List[float]
    sector_labels: List[str]
    sector_weights: List[float]
    tickers: List[str]
    stock_corr: List[List[float]]


@router.post("/charts", response_model=ChartDataResponse)
async def get_charts(req: ChartRequest):
    data = generate_chart_data(req.stocks, req.tickers, req.end_date)
    return data