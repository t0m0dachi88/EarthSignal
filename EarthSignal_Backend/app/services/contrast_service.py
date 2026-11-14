import math
from app.services.ml_service import MLService

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))

class ContrastService:
    def __init__(self, ml: MLService):
        self.ml = ml

    def compare(self, variable: str, cell_a: int, cell_b: int):
        if variable not in self.ml.slope_cols_by_variable():
            raise ValueError("Unsupported variable.")
        a = self.ml.cell(cell_a)
        b = self.ml.cell(cell_b)
        if a is None or b is None:
            raise KeyError("One or both cell IDs were not found.")
        slope_key = f"{variable}_slope"
        distance = haversine_km(a["lat"], a["lon"], b["lat"], b["lon"])
        difference = float(a[slope_key] - b[slope_key])
        opposite = (a[slope_key] > 0 and b[slope_key] < 0) or (a[slope_key] < 0 and b[slope_key] > 0)
        return {
            "variable": variable,
            "cell_a": a,
            "cell_b": b,
            "slope_difference_a_minus_b": difference,
            "opposite_trend_directions": bool(opposite),
            "separation_km": distance,
            "evidence_label": "descriptive_comparison_not_a_pairwise_significance_test",
        }
