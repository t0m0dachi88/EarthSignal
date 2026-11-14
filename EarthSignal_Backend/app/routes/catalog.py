from fastapi import APIRouter
from app.controllers.catalog_controller import get_datasets, get_variables

router = APIRouter(prefix="/catalog", tags=["Catalog"])
@router.get("/datasets")
async def datasets():
    return get_datasets()
@router.get("/variables")
async def variables():
    return get_variables()
