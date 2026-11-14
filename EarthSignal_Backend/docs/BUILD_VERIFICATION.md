# Backend build verification

## Executed in the artifact-building environment

- Python syntax compilation: 48 Python files — PASS.
- Pytest: 10 tests — PASS.
- Actual bundled GLDAS annual NetCDF point extraction: PASS.
- Actual bundled GLDAS regional bounding-box extraction: PASS.
- Actual saved RobustScaler and K-Means Joblib load + prediction smoke test: PASS.
- Model metadata: six input features, three K-Means clusters — PASS.

## Environment limitations

- The build environment did not have PyMongo or PyArrow installed, so the FastAPI process was not started with the complete production dependency set and the Parquet-backed `MLService.load()` was not executed end-to-end here.
- The Joblib smoke test ran under scikit-learn 1.8.0 and emitted the expected version warning because the artifacts were serialized with 1.6.1. The backend requirements pin scikit-learn 1.6.1.
- MongoDB Atlas connectivity, JWT register/login round-trip against Atlas, persistent worker execution and browser integration require installation and the user's private Atlas connection string. These are not claimed as passed.

## Run after setup

```bash
pytest -q
python scripts/init_db.py
```

Then start API and worker in separate terminals and verify `/api/health`, `/api/ml/health`, and `/docs`.
