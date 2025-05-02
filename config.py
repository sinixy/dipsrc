import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATA_PATH: str = os.getenv("DATA_PATH", "model/data/dataset.csv")
    ML_PICKERS_DIR: str = os.getenv("ML_PICKERS_DIR", "model/pickers")
    RISK_MODELS: list[str] = ["mean_variance", "ledoit_wolf", "nco", "equal"]


settings = Settings()