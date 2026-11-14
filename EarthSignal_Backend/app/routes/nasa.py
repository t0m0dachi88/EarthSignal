from fastapi import APIRouter, HTTPException, Query
import httpx
from app.nasa_adapters.cmr import CMRService

router = APIRouter(prefix="/nasa", tags=["NASA metadata"])

@router.get("/collections")
async def search_collections(
    short_name: str | None = None,
    keyword: str | None = None,
    page_size: int = Query(10, ge=1, le=50),
):
    try:
        return await CMRService().collections(short_name, keyword, page_size)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"NASA CMR metadata request failed: {type(exc).__name__}")

@router.get("/granules")
async def search_granules(
    collection_concept_id: str,
    temporal: str | None = None,
    page_size: int = Query(10, ge=1, le=50),
):
    try:
        return await CMRService().granules(collection_concept_id, temporal, page_size)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"NASA CMR granule request failed: {type(exc).__name__}")
