import os
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    DATA_PATH: str = os.getenv("DATA_PATH", "model/data/dataset.csv")
    ML_PICKERS_DIR: str = os.getenv("ML_PICKERS_DIR", "model/pickers")
    RISK_MODELS: list[str] = ["mean_variance", "ledoit_wolf", "nco", "equal"]
    SPY_PATH: str = os.getenv("SPY_PATH", "model/data/spy/spy.csv")
    FINVIZ_API_KEY: str = os.getenv("FINVIZ_API_KEY")
    EXCLUDED_TICKERS: list[str] = ['GOOG']

    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "portfolios")
    PORTFOLIO_COLLECTION: str = os.getenv("PORTFOLIO_COLLECTION", "portfolios")

settings = Settings()