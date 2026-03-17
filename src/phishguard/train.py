"""Train a phishing detector using URL-based features + RandomForest + SMOTE.

Dataset expected:
  - A CSV with at least:
      url,label
    where label is 1 (phishing) or 0 (legit)

Helper scripts provided in scripts/ to convert UCI ARFF -> CSV.
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from .features import extract_url_features, feature_names

@dataclass
class TrainMetrics:
    accuracy: float
    recall_phishing: float
    precision_phishing: float
    f1_phishing: float
    roc_auc: float | None

def featurize_urls(urls: List[str]) -> np.ndarray:
    cols = feature_names()
    X = []
    for u in urls:
        f = extract_url_features(str(u))
        X.append([f[c] for c in cols])
    return np.asarray(X, dtype=float)

def train(csv_path: str, out_dir: str, seed: int = 42) -> Tuple[str, Dict]:
    df = pd.read_csv(csv_path)
    if "url" not in df.columns or "label" not in df.columns:
        raise ValueError("CSV must contain columns: url,label")

    df = df.dropna(subset=["url", "label"]).copy()
    df["label"] = df["label"].astype(int)

    X = featurize_urls(df["url"].tolist())
    y = df["label"].to_numpy(dtype=int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )

    # RandomForest doesn't need scaling; keep pipeline for consistent workflow
    clf = RandomForestClassifier(
        n_estimators=400,
        random_state=seed,
        n_jobs=-1,
        class_weight=None,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
    )

    pipe = ImbPipeline(steps=[
        ("smote", SMOTE(random_state=seed)),
        ("rf", clf),
    ])

    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)

    # Probabilities for AUC if possible
    roc_auc = None
    if hasattr(pipe, "predict_proba"):
        try:
            y_prob = pipe.predict_proba(X_test)[:, 1]
            roc_auc = float(roc_auc_score(y_test, y_prob))
        except Exception:
            roc_auc = None

    # Metrics for phishing class (label=1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, labels=[1], average=None, zero_division=0
    )
    precision_phishing = float(precision[0])
    recall_phishing = float(recall[0])
    f1_phishing = float(f1[0])

    metrics = TrainMetrics(
        accuracy=float(accuracy_score(y_test, y_pred)),
        recall_phishing=recall_phishing,
        precision_phishing=precision_phishing,
        f1_phishing=f1_phishing,
        roc_auc=roc_auc,
    )

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    model_path = str(out / "model.joblib")
    metrics_path = str(out / "metrics.json")

    bundle = {
        "model": pipe,
        "metadata": {
            "model_name": "random_forest_smote",
            "version": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "feature_names": feature_names(),
            "train_csv": os.path.basename(csv_path),
            "seed": seed,
        },
    }
    joblib.dump(bundle, model_path)

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(asdict(metrics), f, indent=2)

    return model_path, {"metrics": asdict(metrics), "classification_report": classification_report(y_test, y_pred, zero_division=0)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to training CSV with columns: url,label")
    ap.add_argument("--out", default="artifacts", help="Output directory for model + metrics")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    model_path, info = train(args.csv, args.out, args.seed)
    print(f"Saved model -> {model_path}")
    print(json.dumps(info["metrics"], indent=2))
    print(info["classification_report"])

if __name__ == "__main__":
    main()
