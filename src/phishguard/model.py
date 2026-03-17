import os
from dataclasses import dataclass
from typing import Any, Dict, Tuple

import joblib

@dataclass
class ModelBundle:
    model: Any
    metadata: Dict[str, Any]

def load_bundle(model_path: str) -> ModelBundle:
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found at '{model_path}'. "
            "Train the model first: python -m phishguard.train --help"
        )
    obj = joblib.load(model_path)
    # Backward compatible: allow either a dict or plain estimator
    if isinstance(obj, dict) and "model" in obj:
        return ModelBundle(model=obj["model"], metadata=obj.get("metadata", {}))
    return ModelBundle(model=obj, metadata={})

def predict_proba(bundle: ModelBundle, X) -> Tuple[int, float, Dict[str, Any]]:
    """Return (label, phishing_probability, extra)."""
    model = bundle.model
    # Prefer predict_proba; fallback to decision_function
    if hasattr(model, "predict_proba"):
        proba = float(model.predict_proba(X)[0, 1])
    elif hasattr(model, "decision_function"):
        # Map decision score to (0,1) via logistic
        import math
        score = float(model.decision_function(X)[0])
        proba = 1.0 / (1.0 + math.exp(-score))
    else:
        proba = float(model.predict(X)[0])
    label = 1 if proba >= 0.5 else 0
    extra = {"threshold": 0.5}
    return label, proba, extra
