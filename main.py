from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import motor.motor_asyncio

from config import settings
from services.updater import run_full_update
from services.dataset import PricesCache
from services.registry import ModelRegistry

from api import pickers, risk, optimize, market, portfolios, user, reminders, stats

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    run_full_update()

    PricesCache.load()

    ModelRegistry.scan(settings.ML_PICKERS_DIR)

    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
    app.state.db = client[settings.MONGODB_DB]

app.include_router(pickers.router, prefix="/model")
app.include_router(risk.router, prefix="/risk")
app.include_router(optimize.router)
app.include_router(market.router)
app.include_router(portfolios.router)
app.include_router(user.router)
app.include_router(reminders.router)
app.include_router(stats.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
