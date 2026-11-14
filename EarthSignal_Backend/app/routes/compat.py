from fastapi import APIRouter, Request, HTTPException
from app.controllers.catalog_controller import get_datasets, get_variables
from app.catalog import VARIABLE_BY_ID
from app.services.science_service import ScienceService

router = APIRouter(tags=["Frontend compatibility"])

@router.get("/datasets")
async def datasets_compat():
    return get_datasets()

@router.get("/variables")
async def variables_compat():
    return get_variables()

@router.get("/discoveries")
async def discoveries_compat(
    request: Request,
    variable: str | None = None,
    integrated_only: bool = False,
    fdr_only: bool = False,
    limit: int = 50,
    offset: int = 0,
):
    ml = request.app.state.ml_service
    if not ml.ready:
        raise HTTPException(status_code=503, detail=ml.error or "ML assets unavailable.")
    if variable and variable not in VARIABLE_BY_ID:
        raise HTTPException(status_code=400, detail="Unsupported variable.")
    if limit < 1 or limit > 200 or offset < 0:
        raise HTTPException(status_code=422, detail="Invalid pagination.")
    return ml.list_discoveries(variable, integrated_only, fdr_only, limit, offset)

@router.get("/trends")
async def trends_compat(
    request: Request,
    variable: str,
    cell_id: int | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    start_year: int = 2003,
    end_year: int = 2023,
):
    if variable not in VARIABLE_BY_ID:
        raise HTTPException(status_code=400, detail="Unsupported variable.")
    if start_year < 2003 or end_year > 2023 or end_year < start_year:
        raise HTTPException(status_code=422, detail="Requested period must be within 2003–2023.")
    if cell_id is not None:
        ml = request.app.state.ml_service
        if not ml.ready:
            raise HTTPException(status_code=503, detail="ML feature assets unavailable.")
        cell = ml.cell(cell_id)
        if cell is None:
            raise HTTPException(status_code=404, detail="Cell not found.")
        latitude, longitude = float(cell["lat"]), float(cell["lon"])
    if latitude is None or longitude is None:
        raise HTTPException(status_code=422, detail="Provide cell_id or latitude and longitude.")
    try:
        service = ScienceService()
        years, values, location = service.point_series(latitude, longitude, variable)
        if cell_id is not None:
            location["cell_id"] = cell_id
        return service.analyze(variable, years, values, location, start_year, end_year)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc))
