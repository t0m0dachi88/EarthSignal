from app.catalog import VARIABLES

RULES = {
    "air_temperature_c": ["surface_temperature_c", "evapotranspiration_mm_month", "topsoil_water_kg_m2"],
    "surface_temperature_c": ["air_temperature_c", "evapotranspiration_mm_month", "rootzone_water_kg_m2"],
    "precipitation_mm_month": ["topsoil_water_kg_m2", "rootzone_water_kg_m2", "evapotranspiration_mm_month"],
    "evapotranspiration_mm_month": ["precipitation_mm_month", "topsoil_water_kg_m2", "rootzone_water_kg_m2"],
    "topsoil_water_kg_m2": ["precipitation_mm_month", "evapotranspiration_mm_month", "rootzone_water_kg_m2"],
    "rootzone_water_kg_m2": ["precipitation_mm_month", "topsoil_water_kg_m2", "evapotranspiration_mm_month"],
}
BY_ID = {v["id"]: v for v in VARIABLES}

class RecommendationService:
    def recommend(self, variable: str, slope: float | None = None):
        if variable not in RULES:
            raise ValueError("Unsupported variable.")
        direction = "increasing" if slope is not None and slope > 0 else "decreasing" if slope is not None and slope < 0 else "changing"
        results = []
        for target in RULES[variable]:
            results.append({
                "suggested_variable": target,
                "name": BY_ID[target]["name"],
                "reason": f"Compare {BY_ID[target]['name'].lower()} with the {direction} {BY_ID[variable]['name'].lower()} pattern.",
                "recommendation_type": "rule_based_scientific_follow_up",
            })
        return {
            "input_variable": variable,
            "input_slope_per_decade": slope,
            "recommendations": results,
            "method": "Transparent domain-rule mapping; no trained NLP model is claimed.",
        }
