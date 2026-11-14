from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.get("/{target_variable}/{cell_a}/{cell_b}")
async def evidence(target_variable: str, cell_a: int, cell_b: int, request: Request):
    ml = request.app.state.ml_service
    if not ml.ready:
        raise HTTPException(status_code=503, detail="ML assets are unavailable.")
    record = ml.discovery(target_variable, cell_a, cell_b)
    if record is None:
        raise HTTPException(status_code=404, detail="No stored validation record for this pair.")
    return {
        "discovery": record,
        "interpretation": {
            "fdr": "Pairwise FDR flag from the supplied exploratory validation workflow.",
            "spatial": "Spatial eligibility is a sensitivity filter; global Moran's I is diagnostic and is not a pairwise spatial correction.",
            "temporal": "Temporal bootstrap results use two short windows and are exploratory.",
        },
        "evidence_label": "exploratory_candidate",
        "source": "NASA GLDAS Noah V2.1, 2003-2023",
    }


@router.get("/{discovery_id}")
async def evidence_by_id(discovery_id: str, request: Request):
    try:
        target, cell_a, cell_b = discovery_id.rsplit(":", 2)
        cell_a, cell_b = int(cell_a), int(cell_b)
    except Exception:
        raise HTTPException(status_code=400, detail="Use target_variable:cell_a:cell_b as discovery_id.")
    ml = request.app.state.ml_service
    if not ml.ready:
        raise HTTPException(status_code=503, detail="ML assets are unavailable.")
    record = ml.discovery(target, cell_a, cell_b)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence record not found.")
    return {
        "discovery_id": discovery_id,
        "discovery": record,
        "evidence_label": "exploratory_candidate",
        "source": "NASA GLDAS Noah V2.1, 2003-2023",
        "limitations": [
            "Pair selection and validation share the historical data; post-selection bias is possible.",
            "Global Moran's I is diagnostic and is not a pairwise spatial correction.",
            "Temporal bootstrap windows are short and exploratory.",
        ],
    }
