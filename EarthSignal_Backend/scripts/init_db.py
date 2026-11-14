import asyncio
from pymongo import AsyncMongoClient
from app.core.config import settings
from app.db.indexes import ensure_indexes

async def main():
    if not settings.mongodb_uri:
        raise RuntimeError("Set MONGODB_URI in .env first.")
    client = AsyncMongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000, appname="EarthSignalInit")
    try:
        await client.admin.command("ping")
        db = client[settings.mongodb_db_name]
        await ensure_indexes(db)
        print(f"Indexes verified for database: {settings.mongodb_db_name}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
