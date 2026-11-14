from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "EarthSignal API"
    app_version: str = "1.0.0"
    environment: str = "development"
    api_prefix: str = "/api"
    secret_key: str = "CHANGE-ME-IN-PRODUCTION-TO-A-LONG-RANDOM-SECRET"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 12
    mongodb_uri: str | None = None
    mongodb_db_name: str = "earthsignal"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    ml_assets_dir: Path = BACKEND_DIR / "data" / "ml_assets"
    annual_netcdf_path: Path = (
        BACKEND_DIR / "data" / "ml_assets" /
        "phase0c_preprocessing" / "features" / "trends" /
        "EarthSignal_annual_anomalies.nc"
    )
    worker_poll_seconds: float = 2.0
    worker_lease_seconds: int = 120
    worker_max_attempts: int = 3
    max_bbox_cells: int = 10000

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
