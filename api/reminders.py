# portfolio_api/api/reminders.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

from services.reminders import (
    get_reminders_for_portfolio,
    toggle_reminder,
    init_scheduler
)

router = APIRouter(
    prefix="/portfolios/{portfolio_id}/reminders",
    tags=["reminders"]
)

@router.on_event("startup")
async def startup_event():
    init_scheduler()

class Reminder(BaseModel):
    id: str = Field(alias="_id")
    portfolio_id: str
    type: str
    job_id: str
    active: bool
    created_at: datetime
    updated_at: datetime

class ReminderUpdate(BaseModel):
    active: bool

@router.get("/", response_model=List[Reminder])
async def list_reminders(portfolio_id: str):
    docs = get_reminders_for_portfolio(portfolio_id)
    return [
        Reminder(**doc) for doc in docs
    ]

@router.put("/{reminder_id}", response_model=Reminder)
async def update_reminder(
    portfolio_id: str,
    reminder_id: str,
    payload: ReminderUpdate
):
    try:
        updated = toggle_reminder(reminder_id, payload.active)
    except ValueError:
        raise HTTPException(status_code=404, detail="Reminder not found")
    # ensure it belongs to this portfolio
    if updated.get("portfolio_id") != portfolio_id:
        raise HTTPException(status_code=400, detail="Mismatched portfolio_id")
    return Reminder(**updated)
