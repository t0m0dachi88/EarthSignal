from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import RecommendationRequest
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("")
async def recommend(payload: RecommendationRequest):
    try:
        return RecommendationService().recommend(payload.variable, payload.slope_per_decade)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{variable}")
async def recommend_by_variable(variable: str, slope_per_decade: float | None = Query(default=None)):
    try:
        return RecommendationService().recommend(variable, slope_per_decade)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
