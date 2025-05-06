from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Any
from datetime import date

from services.charts import generate_chart_data

router = APIRouter(prefix="/stats", tags=["stats"])


class ChartRequest(BaseModel):
    stocks: list[dict]
    tickers: dict[str, Any]
    end_date: date


class ChartDataResponse(BaseModel):
    dates: List[str]
    equity: List[float]
    drawdown: List[float]
    sector_labels: List[str]
    sector_weights: List[float]
    tickers: List[str]
    heatmap_data_points: List[dict]


@router.post("/charts", response_model=ChartDataResponse)
async def get_charts(req: ChartRequest):
    try:
        data = generate_chart_data(req.stocks, req.tickers, req.end_date)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error generating chart data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error generating chart data.")