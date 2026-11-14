from fastapi import APIRouter, Request, HTTPException
from app.db.db import database_status

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health(request: Request):
    db = await database_status(request)
    ml = request.app.state.ml_service.health()
    return {
        "status": "ok",
        "service": "earthsignal-api",
        "database": db,
        "ml_assets": ml,
    }

@router.get("/ready")
async def ready(request: Request):
    db = await database_status(request)
    ml = request.app.state.ml_service.health()
    if not db["connected"]:
        raise HTTPException(status_code=503, detail="MongoDB Atlas is not connected.")
    if not ml["ready"]:
        raise HTTPException(status_code=503, detail="ML assets are not ready.")
    return {"status": "ready", "database": db, "ml_assets": ml}
