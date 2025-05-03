from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import motor.motor_asyncio

from config import settings
from services.dataset import PricesCache
from services.registry import ModelRegistry
from api import pickers, risk, optimize, market, portfolios

app = FastAPI()
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    PricesCache.load(settings.DATA_PATH)
    ModelRegistry.scan(settings.ML_PICKERS_DIR)
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
    app.state.db = client[settings.MONGODB_DB]

# mount routers
app.include_router(pickers.router, prefix="/model")
app.include_router(risk.router, prefix="/risk")
app.include_router(optimize.router)
app.include_router(market.router)
app.include_router(portfolios.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)