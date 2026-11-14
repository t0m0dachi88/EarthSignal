import asyncio
import logging
import os
import socket
from datetime import datetime, timedelta, timezone
from pymongo import AsyncMongoClient, ReturnDocument
from app.core.config import settings
from app.services.ml_service import MLService
from app.services.job_processor import JobProcessor

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("earthsignal.worker")

async def run_worker():
    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is required to run the worker.")
    client = AsyncMongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000, appname="EarthSignalWorker")
    await client.admin.command("ping")
    db = client[settings.mongodb_db_name]
    ml = MLService()
    if not ml.load():
        raise RuntimeError(f"ML assets failed to load: {ml.error}")
    processor = JobProcessor(ml)
    worker_id = f"{socket.gethostname()}:{os.getpid()}"
    log.info("Worker started: %s", worker_id)
    try:
        while True:
            now = datetime.now(timezone.utc)
            job = await db["analysis_runs"].find_one_and_update(
                {
                    "status": "queued",
                    "$or": [{"next_attempt_at": {"$exists": False}}, {"next_attempt_at": {"$lte": now}}],
                },
                {
                    "$set": {
                        "status": "running",
                        "worker_id": worker_id,
                        "lease_expires_at": now + timedelta(seconds=settings.worker_lease_seconds),
                        "started_at": now,
                        "updated_at": now,
                    },
                    "$inc": {"attempts": 1},
                },
                sort=[("created_at", 1)],
                return_document=ReturnDocument.AFTER,
            )
            if not job:
                # Recover expired leases, bounded by attempts.
                await db["analysis_runs"].update_many(
                    {"status": "running", "lease_expires_at": {"$lt": now}, "attempts": {"$lt": settings.worker_max_attempts}},
                    {"$set": {"status": "queued", "next_attempt_at": now, "updated_at": now}, "$unset": {"worker_id": "", "lease_expires_at": ""}},
                )
                exhausted = await db["analysis_runs"].find(
                    {"status": "running", "lease_expires_at": {"$lt": now}, "attempts": {"$gte": settings.worker_max_attempts}}
                ).to_list(length=100)
                for stale in exhausted:
                    await db["analysis_runs"].update_one(
                        {"job_id": stale["job_id"]},
                        {"$set": {"status": "failed", "error": {"message": "Worker lease expired after maximum attempts."}, "updated_at": now}},
                    )
                    await db["investigations"].update_one(
                        {"investigation_id": stale["investigation_id"]},
                        {"$set": {"status": "failed", "error": "Worker lease expired after maximum attempts.", "updated_at": now}},
                    )
                await asyncio.sleep(settings.worker_poll_seconds)
                continue
            try:
                await processor.process(db, job)
            except Exception as exc:
                log.exception("Job failed: %s", job["job_id"])
                attempts = int(job.get("attempts", 1))
                final = attempts >= settings.worker_max_attempts
                state = "failed" if final else "queued"
                now2 = datetime.now(timezone.utc)
                await db["analysis_runs"].update_one(
                    {"job_id": job["job_id"]},
                    {"$set": {
                        "status": state,
                        "error": {"type": type(exc).__name__, "message": str(exc)[:1000]},
                        "updated_at": now2,
                        "next_attempt_at": now2 + timedelta(seconds=min(30 * attempts, 300)),
                    }},
                )
                await db["investigations"].update_one(
                    {"investigation_id": job["investigation_id"]},
                    {"$set": {"status": state, "error": str(exc)[:1000], "updated_at": now2}},
                )
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run_worker())
