from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.db import mongo_lifespan
from app.services.ml_service import MLService
from app.routes import health, catalog, auth, ml, science, investigations, recommendations, evidence, jobs, compat, nasa

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ml_service = MLService()
    app.state.ml_service.load()
    async with mongo_lifespan(app):
        yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NASA GLDAS Earth-system trend discovery and scientific investigation API.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [health.router, catalog.router, auth.router, ml.router, science.router,
               investigations.router, recommendations.router, evidence.router, jobs.router, compat.router, nasa.router]:
    app.include_router(router, prefix=settings.api_prefix)

@app.get("/")
async def root():
    return {"service": "EarthSignal API", "docs": "/docs", "health": f"{settings.api_prefix}/health"}
