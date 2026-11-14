from app.catalog import DATASETS, VARIABLES
def get_datasets():
    return {"items": DATASETS, "count": len(DATASETS)}
def get_variables():
    return {"items": VARIABLES, "count": len(VARIABLES)}
