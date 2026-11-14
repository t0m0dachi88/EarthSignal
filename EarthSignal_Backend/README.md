# EarthSignal Backend — Complete MVP API

This is a new, modular FastAPI backend for EarthSignal. It follows the approved architecture: React/TypeScript frontend → FastAPI → MongoDB Atlas, with Google Colab-trained ML artifacts loaded for inference. **No Docker is used or required.**

## Included

- FastAPI application and OpenAPI docs
- Modular routes, services, controllers, repositories, Pydantic schemas
- Async PyMongo Atlas connection (`app/db/db.py`)
- MongoDB indexes for users, investigations, jobs, discoveries, trends, contrasts, recommendations and model registry
- Argon2 password hashing and expiring JWT access tokens
- Ownership-protected investigations and job status
- Persistent MongoDB-backed background worker (no Redis/Celery)
- Six-variable GLDAS annual anomaly trend extraction from the supplied NetCDF
- Theil–Sen/Kendall exploratory trend calculation
- K-Means/scaler loading, cluster summaries, nearest-region search
- Precomputed discovery catalogue and evidence retrieval
- Rule-based transparent recommendations
- Windows and Unix setup/run scripts
- Real Colab ML asset ZIP included and extracted under `data/ml_assets/`

## Important truth about the data scope

The backend integrates the supplied **GLDAS Noah V2.1 2003–2023** assets and six variables. GPM IMERG, MERRA-2 and MODIS are listed as catalog-only, not ingested or available for analysis. No fake observations are generated.

The ML asset loader uses the saved six-variable RobustScaler and K-Means model. It requires the same scikit-learn version used to create the artifacts (`1.6.1`) and PyArrow for Parquet.

## Setup — Windows PowerShell

From this `EarthSignal_Backend` folder:

```powershell
.\scripts\setup.ps1
```

Edit `.env` and set:
- `SECRET_KEY` to a long random secret
- `MONGODB_URI` to your private MongoDB Atlas connection string
- `MONGODB_DB_NAME=earthsignal`
- `CORS_ORIGINS` to your frontend origin, e.g. `http://localhost:5173`

Start API in PowerShell window 1:

```powershell
.\scripts\run_backend.ps1
```

Start worker in PowerShell window 2:

```powershell
.\scripts\run_worker.ps1
```

Open:
- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health

## Setup — macOS/Linux/WSL

```bash
bash scripts/setup.sh
```

Configure `.env`, then run API and worker in separate terminals:

```bash
bash scripts/run_backend.sh
bash scripts/run_worker.sh
```

## Atlas configuration

Create a MongoDB Atlas database user and allow your machine's IP address in Atlas Network Access. Put the URI in `.env`. Never upload `.env` or commit secrets. Without Atlas:
- `/api/health`, `/api/catalog/*`, `/api/ml/*`, `/api/trends/*`, `/api/contrasts`, `/api/recommendations` can operate if local ML/scientific assets load.
- Registration, login, saved investigations and the background worker return a clear database-not-configured condition.

## Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API, DB and ML health |
| GET | `/api/ready` | Readiness gate |
| GET | `/api/catalog/datasets` | Dataset catalog |
| GET | `/api/catalog/variables` | Six-variable catalog |
| POST | `/api/auth/register` | Register |
| POST | `/api/auth/login` | Get JWT |
| GET | `/api/auth/me` | Current user |
| GET | `/api/ml/health` | ML asset health |
| GET | `/api/ml/metadata` | ML metadata and summary |
| GET | `/api/ml/clusters` | Cluster sizes/profiles |
| GET | `/api/ml/discoveries` | 180 stored candidate pairs with filters |
| GET | `/api/ml/cells/{cell_id}` | Cell features and cluster |
| GET | `/api/ml/similar-regions/{cell_id}` | Similar six-variable signatures |
| GET | `/api/trends/cell/{cell_id}?variable=...` | Annual anomaly series and exploratory trend |
| GET | `/api/trends/point?latitude=...&longitude=...&variable=...` | Nearest grid-cell trend |
| POST | `/api/contrasts` | Compare two cells descriptively |
| GET | `/api/evidence/{variable}/{cell_a}/{cell_b}` | Stored pair validation evidence |
| POST | `/api/recommendations` | Explainable follow-up suggestions |
| POST | `/api/investigations` | Queue an owned investigation (JWT required) |
| GET | `/api/investigations` | List current user's investigations |
| GET | `/api/investigations/{id}` | Get owned investigation |
| GET | `/api/investigations/{id}/results` | Retrieve completed result |
| GET | `/api/jobs/{job_id}` | Get owned job status |

## Example API calls

Register:
```json
{"email":"demo@example.com","password":"Use-a-long-private-password","display_name":"Demo Researcher"}
```

Login returns `access_token`. Send it as:
`Authorization: Bearer <access_token>`.

Create a cell investigation:
```json
{
  "mode": "cell",
  "title": "Air temperature at a GLDAS cell",
  "variable": "air_temperature_c",
  "cell_id": 1234,
  "start_year": 2003,
  "end_year": 2023
}
```

Create a region investigation:
```json
{
  "mode": "place",
  "title": "Regional precipitation",
  "variable": "precipitation_mm_month",
  "bbox": {"west": 88.0, "south": 20.0, "east": 92.0, "north": 27.0}
}
```

## Scientific interpretation

- Theil–Sen slope is calculated from annual anomalies; slope units are the variable's source units per decade.
- Kendall p-values returned by the interactive trend endpoint are **uncorrected exploratory values**. They are not autocorrelation-adjusted or multiple-testing-adjusted.
- Stored pair-level FDR/temporal/spatial fields are displayed as supplied. Global Moran's I is a diagnostic, not a pairwise spatial correction.
- Recommendations are deterministic domain rules, not a trained language model.
- The 45 integrated candidates are not described as proven causal or forecast results.

## Tests

```bash
pytest -q
```

The included tests cover the pure trend function, catalog declarations and password hashing. Live Atlas, real ML Parquet loading, and end-to-end worker execution require installing dependencies and configuring the user's Atlas account.

## Frontend connection

The Vite frontend can proxy `/api` to `http://127.0.0.1:8000`. Use relative URLs such as `/api/ml/discoveries`. CORS defaults allow local Vite development.
