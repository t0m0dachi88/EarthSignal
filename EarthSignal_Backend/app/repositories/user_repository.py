from app.repositories.base import MongoRepository

class UserRepository(MongoRepository):
    def __init__(self, db):
        super().__init__(db, "users")

    async def by_email(self, email: str):
        return await self.collection.find_one({"email": email})

    async def public_by_id(self, user_id: str):
        return await self.collection.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
