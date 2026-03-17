from __future__ import annotations

import time
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, request

from .features import extract_url_features, feature_names
from .model import load_bundle, predict_proba

api_bp = Blueprint("api", __name__)

_bundle_cache = {"path": None, "bundle": None}

def _get_bundle():
    model_path = current_app.config["MODEL_PATH"]
    if _bundle_cache["bundle"] is None or _bundle_cache["path"] != model_path:
        _bundle_cache["bundle"] = load_bundle(model_path)
        _bundle_cache["path"] = model_path
    return _bundle_cache["bundle"]

@api_bp.get("/health")
def health():
    return jsonify({"status": "ok", "schema": current_app.config["SCHEMA_VERSION"]})

@api_bp.post("/predict")
def predict():
    t0 = time.time()
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    url = (payload.get("url") or "").strip()
    if not url:
        return jsonify({
            "error": "Missing required field: url",
            "example": {"url": "https://example.com/login"}
        }), 400

    feats = extract_url_features(url)
    # Convert to 2D array in stable order
    cols = feature_names()
    X = [[feats[c] for c in cols]]

    bundle = _get_bundle()
    label, prob, extra = predict_proba(bundle, X)

    elapsed_ms = int((time.time() - t0) * 1000)
    resp = {
        "url": url,
        "is_phishing": bool(label == 1),
        "phishing_probability": round(prob, 6),
        "model": bundle.metadata.get("model_name", "random_forest"),
        "model_version": bundle.metadata.get("version", "unknown"),
        "latency_ms": elapsed_ms,
        "features": feats if bool(payload.get("debug")) else None,
        "meta": extra,
    }
    # Remove nulls to keep response clean
    resp = {k: v for k, v in resp.items() if v is not None}
    return jsonify(resp), 200
