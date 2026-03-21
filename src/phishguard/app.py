import os
from flask import Flask
from flask_cors import CORS
from .routes import api_bp

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    app.config["MODEL_PATH"] = os.getenv("PHISHGUARD_MODEL_PATH", "artifacts/model.joblib")
    app.config["SCHEMA_VERSION"] = "v1"

    app.register_blueprint(api_bp, url_prefix="/v1")
    return app