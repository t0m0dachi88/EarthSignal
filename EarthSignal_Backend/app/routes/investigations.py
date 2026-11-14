from fastapi import APIRouter, Depends, HTTPException, Query
from app.db.db import get_database
from app.core.security import get_current_user
from app.models.schemas import InvestigationCreate
from app.services.investigation_service import InvestigationService

router = APIRouter(prefix="/investigations", tags=["Investigations"])

@router.post("", status_code=202)
async def create_investigation(payload: InvestigationCreate, user=Depends(get_current_user), db=Depends(get_database)):
    from app.catalog import VARIABLE_BY_ID
    if payload.variable not in VARIABLE_BY_ID:
        raise HTTPException(status_code=400, detail="Unsupported variable.")
    if payload.mode == "cell" and payload.cell_id is None and (payload.latitude is None or payload.longitude is None):
        raise HTTPException(status_code=422, detail="Cell mode requires cell_id or latitude/longitude.")
    if payload.mode == "contrast" and (payload.cell_id is None or payload.comparison_cell_id is None):
        raise HTTPException(status_code=422, detail="Contrast mode requires cell_id and comparison_cell_id.")
    if payload.mode == "place" and payload.bbox is None and payload.cell_id is None and payload.latitude is None:
        raise HTTPException(status_code=422, detail="Place mode requires bbox, cell_id, or coordinates.")
    return await InvestigationService(db).create(payload, user)

@router.get("")
async def list_investigations(
    limit: int = Query(20, ge=1, le=100),
    user=Depends(get_current_user),
    db=Depends(get_database),
):
    cursor = db["investigations"].find({"owner_id": user["user_id"]}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return {"items": await cursor.to_list(length=limit)}

@router.get("/{investigation_id}")
async def get_investigation(investigation_id: str, user=Depends(get_current_user), db=Depends(get_database)):
    return await InvestigationService(db).get(investigation_id, user)

@router.get("/{investigation_id}/results")
async def get_results(investigation_id: str, user=Depends(get_current_user), db=Depends(get_database)):
    return await InvestigationService(db).result(investigation_id, user)
