from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, db):
        self.users = UserRepository(db)

    async def register(self, payload):
        if await self.users.by_email(payload.email):
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        user = {
            "user_id": str(uuid4()),
            "email": payload.email,
            "display_name": payload.display_name.strip(),
            "password_hash": hash_password(payload.password),
            "role": "user",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
        }
        await self.users.collection.insert_one(user)
        return {k: user[k] for k in ("user_id", "email", "display_name", "role")}

    async def login(self, email: str, password: str):
        user = await self.users.by_email(email.strip().lower())
        if not user or user.get("status") != "active" or not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password.")
        return {
            "access_token": create_access_token(user["user_id"], user["role"]),
            "token_type": "bearer",
            "expires_in": settings.access_token_minutes * 60,
        }
