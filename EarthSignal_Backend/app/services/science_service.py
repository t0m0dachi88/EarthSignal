from __future__ import annotations
from pathlib import Path
import h5py
import numpy as np
from scipy.stats import theilslopes, kendalltau
from app.core.config import settings
from app.catalog import VARIABLE_BY_ID

class ScienceService:
    """Reads the bundled annual GLDAS anomaly NetCDF/HDF5 file directly."""
    def __init__(self):
        self.dataset_path = Path(settings.annual_netcdf_path)

    def _open(self):
        if not self.dataset_path.is_file():
            raise FileNotFoundError(f"Annual anomaly NetCDF not found: {self.dataset_path}")
        return h5py.File(self.dataset_path, "r")

    def point_series(self, latitude: float, longitude: float, variable: str):
        if variable not in VARIABLE_BY_ID:
            raise ValueError("Unsupported variable.")
        with self._open() as ds:
            if variable not in ds:
                raise ValueError(f"Variable {variable} is not in the annual dataset.")
            latitudes = ds["lat"][:]
            longitudes = ds["lon"][:]
            lat_idx = int(np.abs(latitudes - latitude).argmin())
            lon_idx = int(np.abs(longitudes - longitude).argmin())
            values = np.asarray(ds[variable][:, lat_idx, lon_idx], dtype=float)
            years = np.asarray(ds["year"][:], dtype=int)
            actual_lat = float(latitudes[lat_idx])
            actual_lon = float(longitudes[lon_idx])
        return years, values, {"latitude": actual_lat, "longitude": actual_lon, "cells_used": 1}

    def bbox_series(self, bbox: dict, variable: str):
        if variable not in VARIABLE_BY_ID:
            raise ValueError("Unsupported variable.")
        with self._open() as ds:
            if variable not in ds:
                raise ValueError(f"Variable {variable} is not in the annual dataset.")
            latitudes = ds["lat"][:]
            longitudes = ds["lon"][:]
            lat_idx = np.where((latitudes >= bbox["south"]) & (latitudes <= bbox["north"]))[0]
            lon_idx = np.where((longitudes >= bbox["west"]) & (longitudes <= bbox["east"]))[0]
            cells = int(len(lat_idx) * len(lon_idx))
            if cells == 0:
                raise ValueError("The requested bounding box contains no grid cells.")
            if cells > settings.max_bbox_cells:
                raise ValueError(f"Bounding box is too large ({cells} grid cells); reduce its size.")
            # Read the selected window only. The NetCDF grid has ascending lat/lon coordinates.
            block = np.asarray(ds[variable][:, lat_idx.min():lat_idx.max()+1, lon_idx.min():lon_idx.max()+1], dtype=float)
            lat_local = lat_idx - lat_idx.min()
            lon_local = lon_idx - lon_idx.min()
            block = block[:, lat_local, :][:, :, lon_local]
            values = np.nanmean(block, axis=(1, 2))
            years = np.asarray(ds["year"][:], dtype=int)
        return years, values, {"cells_used": cells, "bbox": bbox}

    @staticmethod
    def calculate_trend(years, values):
        mask = np.isfinite(years) & np.isfinite(values)
        x = np.asarray(years)[mask].astype(float)
        y = np.asarray(values)[mask].astype(float)
        if len(x) < 8:
            return {
                "classification": "insufficient_data",
                "observation_count": int(len(x)),
                "slope_per_decade": None,
                "kendall_tau": None,
                "p_value_uncorrected": None,
                "confidence_interval_95_per_decade": None,
            }
        slope, intercept, low, high = theilslopes(y, x, alpha=0.95)
        tau, p = kendalltau(x, y, nan_policy="omit")
        slope10 = float(slope * 10)
        ci = [float(low * 10), float(high * 10)]
        return {
            "classification": "increasing" if slope > 0 else "decreasing" if slope < 0 else "no_direction",
            "observation_count": int(len(x)),
            "slope_per_decade": slope10,
            "kendall_tau": float(tau) if np.isfinite(tau) else None,
            "p_value_uncorrected": float(p) if np.isfinite(p) else None,
            "confidence_interval_95_per_decade": ci,
            "method": "Theil-Sen slope and Kendall tau on annual anomalies",
            "inference_note": "Exploratory uncorrected p-value; not adjusted for temporal autocorrelation or multiple testing.",
        }

    def analyze(self, variable: str, years, values, location: dict, start_year=None, end_year=None):
        y_all = np.asarray(years, dtype=int)
        v_all = np.asarray(values, dtype=float)
        start = int(start_year if start_year is not None else y_all.min())
        end = int(end_year if end_year is not None else y_all.max())
        keep = (y_all >= start) & (y_all <= end)
        y = y_all[keep]
        v = v_all[keep]
        if len(y) == 0:
            raise ValueError("No annual observations fall within the requested period.")
        trend = self.calculate_trend(y, v)
        return {
            "variable": variable,
            "variable_name": VARIABLE_BY_ID[variable]["name"],
            "units": VARIABLE_BY_ID[variable]["units"],
            "source": "NASA GLDAS Noah V2.1",
            "period": {"start_year": int(y[0]), "end_year": int(y[-1])},
            "location": location,
            "time_series": [{"year": int(a), "anomaly": None if not np.isfinite(b) else float(b)} for a, b in zip(y, v)],
            "trend": trend,
            "evidence_label": "exploratory_historical_analysis",
        }
