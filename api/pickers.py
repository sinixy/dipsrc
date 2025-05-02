from fastapi import APIRouter
from services.registry import ModelRegistry

router = APIRouter()

@router.get("/pickers")
def list_pickers():
    return ModelRegistry.list_pickers()
