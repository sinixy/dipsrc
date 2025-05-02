from fastapi import APIRouter
from services.registry import ModelRegistry

router = APIRouter()

@router.get("/models")
def list_risk_models():
    return ModelRegistry.list_risk_models()