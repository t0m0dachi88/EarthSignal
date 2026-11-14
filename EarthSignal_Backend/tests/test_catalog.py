from app.catalog import VARIABLES, DATASETS, VARIABLE_BY_ID

def test_six_gldas_variables_are_available():
    assert len(VARIABLES) == 6
    assert all(v["available"] for v in VARIABLES)

def test_gldas_dataset_is_marked_integrated():
    gldas = next(d for d in DATASETS if d["id"] == "GLDAS_NOAH025_M")
    assert gldas["status"] == "integrated_assets_available"
    assert len(gldas["variables"]) == 6

def test_other_products_are_not_claimed_ingested():
    others = [d for d in DATASETS if d["id"] != "GLDAS_NOAH025_M"]
    assert all(d["status"] == "catalog_only_not_ingested" for d in others)
