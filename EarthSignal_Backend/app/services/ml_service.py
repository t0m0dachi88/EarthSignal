from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.neighbors import NearestNeighbors
from app.core.config import settings
from app.catalog import VARIABLES

class MLAssetError(RuntimeError):
    pass

class MLService:
    def __init__(self):
        self.ready = False
        self.error = None
        self.features = None
        self.discoveries = None
        self.integrated = None
        self.scaler = None
        self.kmeans = None
        self.neighbors = None
        self.profiles = None
        self.summary = {}
        self.metadata = {}
        self.cell_rows = {}
        self.labels = None
        self.scaled_cols = [f'{v["id"]}_scaled' for v in VARIABLES]
        self.slope_cols = [f'{v["id"]}_slope' for v in VARIABLES]

    def load(self):
        root = Path(settings.ml_assets_dir)
        required = {
            "features": root / "phase0e_ml_features/EarthSignal_ML_Features.parquet",
            "scaler": root / "phase0e_ml_features/EarthSignal_RobustScaler.joblib",
            "metadata": root / "phase0e_ml_features/EarthSignal_Feature_Metadata.json",
            "kmeans": root / "phase0f_clustering/EarthSignal_KMeans.joblib",
            "profiles": root / "phase0f_clustering/EarthSignal_Cluster_Profiles.csv",
            "integrated": root / "phase0g_validation/EarthSignal_Integrated_Discovery_Evaluation.csv",
            "summary": root / "phase0g_validation/EarthSignal_Final_ML_Results_Summary.json",
        }
        missing = [str(p) for p in required.values() if not p.is_file()]
        if missing:
            self.error = "Missing ML assets: " + ", ".join(missing)
            return False
        try:
            self.features = pd.read_parquet(required["features"])
            self.integrated = pd.read_csv(required["integrated"])
            self.discoveries = pd.read_csv(root / "phase0f_contrast_discovery/EarthSignal_Contrasting_Patterns.csv")
            self.scaler = joblib.load(required["scaler"])
            self.kmeans = joblib.load(required["kmeans"])
            self.profiles = pd.read_csv(required["profiles"])
            self.metadata = json.loads(required["metadata"].read_text(encoding="utf-8"))
            self.summary = json.loads(required["summary"].read_text(encoding="utf-8"))
            for col in ["cell_id", "lat", "lon", *self.scaled_cols, *self.slope_cols]:
                if col not in self.features.columns:
                    raise ValueError(f"Feature parquet missing column: {col}")
            if self.features["cell_id"].duplicated().any():
                raise ValueError("Duplicate cell_id in feature parquet.")
            expected_cells = self.metadata.get("n_cells")
            if expected_cells is not None and len(self.features) != int(expected_cells):
                raise ValueError(f"Feature row count {len(self.features)} != metadata n_cells {expected_cells}.")
            matrix = self.features[self.scaled_cols].to_numpy(dtype=float)
            if not np.isfinite(matrix).all():
                raise ValueError("Scaled feature matrix contains non-finite values.")
            if getattr(self.kmeans, "n_features_in_", None) != 6:
                raise ValueError("KMeans model feature count is not six.")
            if getattr(self.scaler, "n_features_in_", None) != 6:
                raise ValueError("RobustScaler feature count is not six.")
            self.labels = self.kmeans.predict(matrix)
            self.cell_rows = {int(cid): i for i, cid in enumerate(self.features["cell_id"].tolist())}
            self.neighbors = NearestNeighbors(metric="euclidean").fit(matrix)
            self.ready = True
            self.error = None
            return True
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"
            self.ready = False
            return False

    def slope_cols_by_variable(self):
        return {c.removesuffix("_slope"): c for c in self.slope_cols}

    def health(self):
        return {
            "ready": self.ready,
            "artifact_version": "earthsignal-gldas-2003-2023-ml-v1",
            "cells": len(self.features) if self.features is not None else 0,
            "discoveries": len(self.integrated) if self.integrated is not None else 0,
            "clusters": int(len(set(self.labels.tolist()))) if self.labels is not None else 0,
            "error": self.error,
        }

    def _check(self):
        if not self.ready:
            raise RuntimeError(self.error or "ML assets are not available.")

    def cell(self, cell_id: int):
        self._check()
        idx = self.cell_rows.get(int(cell_id))
        if idx is None:
            return None
        row = self.features.iloc[idx].to_dict()
        row["cluster_id"] = int(self.labels[idx])
        return _clean(row)

    def clusters(self):
        self._check()
        counts = pd.Series(self.labels).value_counts().sort_index()
        profiles = self.profiles.to_dict(orient="records")
        return [
            {
                "cluster_id": int(cid),
                "cell_count": int(count),
                "profile": next((p for p in profiles if int(p["cluster_id"]) == int(cid)), None),
            }
            for cid, count in counts.items()
        ]

    def similar(self, cell_id: int, limit: int = 10):
        self._check()
        idx = self.cell_rows.get(int(cell_id))
        if idx is None:
            return None
        k = min(len(self.features), limit + 1)
        distances, indices = self.neighbors.kneighbors(
            self.features.iloc[[idx]][self.scaled_cols].to_numpy(dtype=float), n_neighbors=k
        )
        result = []
        for dist, i in zip(distances[0], indices[0]):
            if int(i) == idx:
                continue
            rec = self.cell(int(self.features.iloc[int(i)]["cell_id"]))
            rec["similarity_distance"] = float(dist)
            result.append(rec)
            if len(result) >= limit:
                break
        return result

    def list_discoveries(self, variable=None, integrated_only=False, fdr_only=False, limit=50, offset=0):
        self._check()
        df = self.integrated.copy()
        if variable:
            df = df[df.target_variable == variable]
        if integrated_only:
            df = df[df.integrated_candidate_flag.astype(bool)]
        if fdr_only:
            df = df[df.fdr_significant.astype(bool)]
        total = len(df)
        items = df.iloc[offset:offset+limit].to_dict(orient="records")
        return {"total": total, "items": _clean(items), "offset": offset, "limit": limit}

    def discovery(self, target_variable: str, cell_a: int, cell_b: int):
        self._check()
        df = self.integrated
        found = df[
            (df.target_variable == target_variable)
            & (df.cell_a == cell_a)
            & (df.cell_b == cell_b)
        ]
        return None if found.empty else _clean(found.iloc[0].to_dict())

def _clean(value):
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    return value
