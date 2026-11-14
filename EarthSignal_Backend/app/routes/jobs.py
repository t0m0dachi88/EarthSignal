from fastapi import APIRouter, Depends, HTTPException
from app.db.db import get_database
from app.core.security import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/{job_id}")
async def job_status(job_id: str, user=Depends(get_current_user), db=Depends(get_database)):
    job = await db["analysis_runs"].find_one(
        {"job_id": job_id, "owner_id": user["user_id"]}, {"_id": 0}
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
