from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError
from fastapi import Request, HTTPException
from app.core.config import settings

@asynccontextmanager
async def mongo_lifespan(app):
    app.state.mongo_client = None
    app.state.db = None
    if settings.mongodb_uri:
        client = AsyncMongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
            appname="EarthSignal",
        )
        try:
            await client.admin.command("ping")
            app.state.mongo_client = client
            app.state.db = client[settings.mongodb_db_name]
            from app.db.indexes import ensure_indexes
            await ensure_indexes(app.state.db)
        except Exception:
            await client.close()
            app.state.mongo_client = None
            app.state.db = None
            if settings.environment.lower() == "production":
                raise
    elif settings.environment.lower() == "production":
        raise RuntimeError("MONGODB_URI is required in production.")
    try:
        yield
    finally:
        if app.state.mongo_client is not None:
            await app.state.mongo_client.close()

async def get_database(request: Request):
    db = getattr(request.app.state, "db", None)
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not configured. Set MONGODB_URI in backend/.env.")
    return db

async def database_status(request: Request) -> dict:
    db = getattr(request.app.state, "db", None)
    client = getattr(request.app.state, "mongo_client", None)
    if db is None or client is None:
        return {"connected": False, "database": settings.mongodb_db_name}
    try:
        await client.admin.command("ping")
        return {"connected": True, "database": settings.mongodb_db_name}
    except PyMongoError:
        return {"connected": False, "database": settings.mongodb_db_name}
