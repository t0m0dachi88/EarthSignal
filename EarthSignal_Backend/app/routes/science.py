from fastapi import APIRouter, Request, HTTPException, Query
from app.catalog import VARIABLE_BY_ID
from app.services.science_service import ScienceService
from app.services.contrast_service import ContrastService
from app.models.schemas import ContrastRequest

router = APIRouter(tags=["Scientific analysis"])

@router.get("/trends/cell/{cell_id}")
async def cell_trend(cell_id: int, variable: str, request: Request, start_year: int = 2003, end_year: int = 2023):
    if variable not in VARIABLE_BY_ID:
        raise HTTPException(status_code=400, detail="Unsupported variable.")
    ml = request.app.state.ml_service
    if not ml.ready:
        raise HTTPException(status_code=503, detail="ML feature assets are unavailable.")
    cell = ml.cell(cell_id)
    if cell is None:
        raise HTTPException(status_code=404, detail="Cell not found.")
    try:
        years, values, location = ScienceService().point_series(cell["lat"], cell["lon"], variable)
        return ScienceService().analyze(variable, years, values, location | {"cell_id": cell_id}, start_year, end_year)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc))

@router.get("/trends/point")
async def point_trend(latitude: float, longitude: float, variable: str, request: Request, start_year: int = 2003, end_year: int = 2023):
    if variable not in VARIABLE_BY_ID:
        raise HTTPException(status_code=400, detail="Unsupported variable.")
    try:
        service = ScienceService()
        years, values, location = service.point_series(latitude, longitude, variable)
        return service.analyze(variable, years, values, location, start_year, end_year)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc))

@router.post("/contrasts")
async def compare(payload: ContrastRequest, request: Request):
    if payload.variable not in VARIABLE_BY_ID:
        raise HTTPException(status_code=400, detail="Unsupported variable.")
    try:
        return ContrastService(request.app.state.ml_service).compare(payload.variable, payload.cell_a, payload.cell_b)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
