import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Secret key for session signing — change this to a strong random value in production
    SECRET_KEY = os.environ.get("SECRET_KEY", "thesis-mvp-secret-key-change-me")

    # SQLite database — absolute path so it works regardless of working directory
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ML model paths
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml", "model.joblib")
    METRICS_PATH = os.path.join(os.path.dirname(__file__), "ml", "metrics.json")
    FEATURE_SCHEMA_PATH = os.path.join(
        os.path.dirname(__file__), "ml", "feature_schema.json"
    )
