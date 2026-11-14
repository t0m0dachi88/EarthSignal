# Architecture

React + TypeScript → FastAPI → MongoDB Atlas. Scientific data and model artifacts are versioned files outside MongoDB. Google Colab remains the training environment; FastAPI loads the exported scaler and K-Means artifact at process startup.

The API process and the persistent worker are separate native Python processes. The worker claims jobs atomically from MongoDB `analysis_runs`, processes them, and persists results. No Docker, Redis or Celery is required for this MVP.
