import numpy as np
from app.services.science_service import ScienceService

def test_theil_sen_positive_trend():
    years = np.arange(2003, 2024)
    values = 0.2 * (years - 2003)
    result = ScienceService.calculate_trend(years, values)
    assert result["classification"] == "increasing"
    assert abs(result["slope_per_decade"] - 2.0) < 1e-8

def test_theil_sen_negative_trend():
    years = np.arange(2003, 2024)
    values = -0.3 * (years - 2003)
    result = ScienceService.calculate_trend(years, values)
    assert result["classification"] == "decreasing"
    assert abs(result["slope_per_decade"] + 3.0) < 1e-8

def test_insufficient_series():
    result = ScienceService.calculate_trend(np.arange(5), np.arange(5))
    assert result["classification"] == "insufficient_data"
