from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime

from config import settings

class UserUpdate(BaseModel):
    telegram_id: int
    email: str

class User(BaseModel):
    id: int
    telegram_id: int
    email: str
    updated_at: datetime

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/", response_model=User)
async def get_user(request: Request):
    db = request.app.state.db
    doc = await db[settings.USER_COLLECTION].find_one({"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**doc)

@router.put("/", response_model=User)
async def update_user(user: UserUpdate, request: Request):
    db = request.app.state.db
    now = datetime.now()
    update_data = {
        "telegram_id": user.telegram_id,
        "email": user.email,
        "updated_at": now,
    }
    result = await db[settings.USER_COLLECTION].update_one(
        {"_id": 0},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return User(
        id=0,
        telegram_id=user.telegram_id,
        email=user.email,
        updated_at=now
    )