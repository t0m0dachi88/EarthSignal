from fastapi import APIRouter, Depends
from app.db.db import get_database
from app.core.security import get_current_user
from app.models.schemas import RegisterRequest, LoginRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=201)
async def register(payload: RegisterRequest, db=Depends(get_database)):
    return await AuthService(db).register(payload)

@router.post("/login")
async def login(payload: LoginRequest, db=Depends(get_database)):
    return await AuthService(db).login(payload.email, payload.password)

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user
