from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from app.repositories.investigation_repository import InvestigationRepository

class InvestigationService:
    def __init__(self, db):
        self.db = db
        self.investigations = InvestigationRepository(db)

    async def create(self, payload, user):
        now = datetime.now(timezone.utc)
        investigation_id, job_id = str(uuid4()), str(uuid4())
        request = payload.model_dump()
        doc = {
            "investigation_id": investigation_id,
            "owner_id": user["user_id"],
            "title": payload.title,
            "mode": payload.mode,
            "question": payload.question,
            "request": request,
            "status": "queued",
            "created_at": now,
            "updated_at": now,
        }
        job = {
            "job_id": job_id,
            "investigation_id": investigation_id,
            "owner_id": user["user_id"],
            "job_type": "investigation",
            "payload": request,
            "status": "queued",
            "attempts": 0,
            "max_attempts": 3,
            "created_at": now,
            "updated_at": now,
        }
        await self.db["investigations"].insert_one(doc)
        await self.db["analysis_runs"].insert_one(job)
        return {
            "investigation_id": investigation_id,
            "job_id": job_id,
            "status": "queued",
            "created_at": now,
        }

    async def get(self, investigation_id: str, user):
        doc = await self.investigations.owned(investigation_id, user["user_id"])
        if not doc:
            raise HTTPException(status_code=404, detail="Investigation not found.")
        return doc

    async def result(self, investigation_id: str, user):
        doc = await self.get(investigation_id, user)
        if doc.get("status") != "completed":
            return {"investigation_id": investigation_id, "status": doc.get("status"), "result": None}
        return {"investigation_id": investigation_id, "status": "completed", "result": doc.get("result")}
