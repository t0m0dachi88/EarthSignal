from typing import Any

class MongoRepository:
    def __init__(self, db, collection: str):
        self.collection = db[collection]

    async def insert(self, document: dict) -> dict:
        await self.collection.insert_one(document)
        return document

    async def get(self, field: str, value: Any) -> dict | None:
        return await self.collection.find_one({field: value}, {"_id": 0})

    async def list(self, query: dict, limit: int = 50, sort=None) -> list[dict]:
        cursor = self.collection.find(query, {"_id": 0})
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.limit(limit).to_list(length=limit)
