from app.repositories.base import MongoRepository

class InvestigationRepository(MongoRepository):
    def __init__(self, db):
        super().__init__(db, "investigations")

    async def owned(self, investigation_id: str, owner_id: str):
        return await self.collection.find_one(
            {"investigation_id": investigation_id, "owner_id": owner_id},
            {"_id": 0},
        )
