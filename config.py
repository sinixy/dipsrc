import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DB_PATH: str = os.getenv("DB_PATH", "model/data/data.db")

    ML_PICKERS_DIR: str = os.getenv("ML_PICKERS_DIR", "model/pickers")
    RISK_MODELS: list[str] = ["mean_variance", "ledoit_wolf", "nco", "equal"]

    FINVIZ_API_KEY: str = os.getenv("FINVIZ_API_KEY")

    EXCLUDED_TICKERS: list[str] = ['GOOG']

    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "portfolios")
    PORTFOLIO_COLLECTION: str = os.getenv("PORTFOLIO_COLLECTION", "portfolios")
    USER_COLLECTION: str = os.getenv("USER_COLLECTION", "user")
    REMINDER_COLLECTION: str = os.getenv("REMINDER_COLLECTION", "reminders")
    JOBSTORE_COLLECTION: str = os.getenv("JOBSTORE_COLLECTION", "apscheduler_jobs")
    UPDATES_COLLECTION: str = os.getenv("UPDATES_COLLECTION", "updates")


settings = Settings()
