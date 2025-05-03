from fastapi import APIRouter, HTTPException
from services.market import get_fear_and_greed, get_vix_info

router = APIRouter(prefix="/market", tags=["market"])

@router.get("/fear_greed", summary="CNN Fear & Greed Index timeseries")
async def fear_greed():
    try:
        data = await get_fear_and_greed()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error fetching Fear & Greed: {e}")
    return data

@router.get("/vix", summary="VIX index metadata from Yahoo Finance")
def vix():
    try:
        vix = get_vix_info()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error fetching VIX info: {e}")
    return {"vix": vix}
