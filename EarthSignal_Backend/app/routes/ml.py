from fastapi import APIRouter, Request, HTTPException, Query
from app.catalog import VARIABLE_BY_ID

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

def get_ml(request: Request):
    ml = request.app.state.ml_service
    if not ml.ready:
        raise HTTPException(status_code=503, detail=ml.error or "ML assets are unavailable.")
    return ml

@router.get("/health")
async def health(request: Request):
    return request.app.state.ml_service.health()

@router.get("/metadata")
async def metadata(request: Request):
    ml = get_ml(request)
    return {"metadata": ml.metadata, "summary": ml.summary, "artifact_version": "earthsignal-gldas-2003-2023-ml-v1"}

@router.get("/clusters")
async def clusters(request: Request):
    return {"items": get_ml(request).clusters()}

@router.get("/cells/{cell_id}")
async def cell(cell_id: int, request: Request):
    result = get_ml(request).cell(cell_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Cell not found.")
    return result

@router.get("/similar-regions/{cell_id}")
async def similar(cell_id: int, request: Request, limit: int = Query(10, ge=1, le=50)):
    result = get_ml(request).similar(cell_id, limit)
    if result is None:
        raise HTTPException(status_code=404, detail="Cell not found.")
    return {"reference_cell_id": cell_id, "items": result, "method": "Nearest neighbours in six-variable RobustScaler feature space."}

@router.get("/discoveries")
async def discoveries(
    request: Request,
    variable: str | None = None,
    integrated_only: bool = False,
    fdr_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    if variable and variable not in VARIABLE_BY_ID:
        raise HTTPException(status_code=400, detail="Unsupported variable.")
    return get_ml(request).list_discoveries(variable, integrated_only, fdr_only, limit, offset)

@router.get("/discoveries/{target_variable}/{cell_a}/{cell_b}")
async def discovery_detail(target_variable: str, cell_a: int, cell_b: int, request: Request):
    result = get_ml(request).discovery(target_variable, cell_a, cell_b)
    if result is None:
        raise HTTPException(status_code=404, detail="Discovery pair not found.")
    return result
