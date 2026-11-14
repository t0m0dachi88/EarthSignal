from pathlib import Path
import warnings
import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / "data" / "ml_assets"

def test_saved_scaler_and_kmeans_artifacts_predict():
    scaler_path = ROOT / "phase0e_ml_features/EarthSignal_RobustScaler.joblib"
    model_path = ROOT / "phase0f_clustering/EarthSignal_KMeans.joblib"
    assert scaler_path.is_file() and model_path.is_file()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        scaler = joblib.load(scaler_path)
        model = joblib.load(model_path)
    assert scaler.n_features_in_ == 6
    assert model.n_features_in_ == 6
    assert model.n_clusters == 3
    sample = np.zeros((2, 6), dtype=float)
    prediction = model.predict(scaler.transform(sample))
    assert prediction.shape == (2,)
