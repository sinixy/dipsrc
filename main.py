from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool

import pandas as pd
import uvicorn

from config import settings
from services.dataset import PricesCache
from services.registry import ModelRegistry
from api import pickers, risk, optimize

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # load full price history into cache
    PricesCache.load(settings.DATA_PATH)
    # discover available ML pickers
    ModelRegistry.scan(settings.ML_PICKERS_DIR)

# mount routers
app.include_router(pickers.router, prefix="/model")
app.include_router(risk.router, prefix="/risk")
app.include_router(optimize.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)