from app.services.science_service import ScienceService


def test_real_bundled_gldas_point_series():
    service = ScienceService()
    years, values, location = service.point_series(27.0, 90.0, "air_temperature_c")
    assert len(years) == 21
    assert int(years[0]) == 2003 and int(years[-1]) == 2023
    assert len(values) == 21
    assert -15 <= location["latitude"] <= 45


def test_real_bundled_gldas_bbox_series():
    service = ScienceService()
    years, values, location = service.bbox_series(
        {"west": 88.0, "south": 20.0, "east": 92.0, "north": 27.0},
        "precipitation_mm_month",
    )
    assert len(years) == 21
    assert location["cells_used"] > 0
