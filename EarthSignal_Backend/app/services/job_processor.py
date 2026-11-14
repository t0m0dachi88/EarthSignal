from datetime import datetime, timezone
from uuid import uuid4
from app.services.science_service import ScienceService
from app.services.ml_service import MLService

class JobProcessor:
    def __init__(self, ml: MLService):
        self.ml = ml
        self.science = ScienceService()

    async def process(self, db, job: dict):
        payload = job["payload"]
        variable = payload["variable"]
        if payload.get("mode") == "contrast" or payload.get("comparison_cell_id") is not None:
            cell_a = int(payload["cell_id"])
            cell_b = int(payload["comparison_cell_id"])
            a, b = self.ml.cell(cell_a), self.ml.cell(cell_b)
            if a is None or b is None:
                raise ValueError("Unknown cell_id in contrast investigation.")
            from app.services.contrast_service import haversine_km
            slope_col = f"{variable}_slope"
            result = {
                "type": "contrast",
                "variable": variable,
                "cell_a": a,
                "cell_b": b,
                "slope_difference": float(a[slope_col] - b[slope_col]),
                "separation_km": haversine_km(a["lat"], a["lon"], b["lat"], b["lon"]),
                "evidence_label": "exploratory_descriptive_contrast",
            }
        elif payload.get("bbox"):
            years, values, location = self.science.bbox_series(payload["bbox"], variable)
            result = self.science.analyze(variable, years, values, location, payload.get("start_year"), payload.get("end_year"))
        else:
            if payload.get("cell_id") is not None:
                cell = self.ml.cell(int(payload["cell_id"]))
                if cell is None:
                    raise ValueError("Unknown cell_id.")
                lat, lon = float(cell["lat"]), float(cell["lon"])
            else:
                lat, lon = payload.get("latitude"), payload.get("longitude")
            if lat is None or lon is None:
                raise ValueError("Provide cell_id, latitude/longitude, or bbox.")
            years, values, location = self.science.point_series(lat, lon, variable)
            result = self.science.analyze(variable, years, values, location, payload.get("start_year"), payload.get("end_year"))
        now = datetime.now(timezone.utc)
        result_doc = {
            "result_id": str(uuid4()),
            "investigation_id": job["investigation_id"],
            "owner_id": job["owner_id"],
            "result": result,
            "created_at": now,
        }
        await db["trend_results"].update_one(
            {"investigation_id": job["investigation_id"]},
            {"$set": result_doc},
            upsert=True,
        )
        await db["investigations"].update_one(
            {"investigation_id": job["investigation_id"]},
            {"$set": {"status": "completed", "result": result, "updated_at": now}},
        )
        await db["analysis_runs"].update_one(
            {"job_id": job["job_id"]},
            {"$set": {"status": "completed", "finished_at": now, "updated_at": now}},
        )
        return result
