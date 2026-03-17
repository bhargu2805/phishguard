import os
import tempfile
import json

import numpy as np
import joblib
import pytest

from phishguard import create_app


# Moved to module level to fix Python 3.14 pickling restriction
class DummyModel:
    def predict_proba(self, X):
        # simple heuristic: longer URLs -> more phishing-ish
        probs = []
        for row in X:
            url_len = row[0]  # url_length is first feature in our extractor
            p = min(max((url_len - 20.0) / 200.0, 0.05), 0.95)
            probs.append([1 - p, p])
        return np.array(probs)


@pytest.fixture()
def app(tmp_path):
    model_path = tmp_path / "model.joblib"
    joblib.dump({"model": DummyModel(), "metadata": {"model_name": "dummy", "version": "test"}}, model_path)

    os.environ["PHISHGUARD_MODEL_PATH"] = str(model_path)
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_health(client):
    r = client.get("/v1/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"


def test_predict_validation(client):
    r = client.post("/v1/predict", json={})
    assert r.status_code == 400


def test_predict_ok(client):
    r = client.post("/v1/predict", json={"url": "http://example.com"})
    assert r.status_code == 200
    data = r.get_json()
    assert "phishing_probability" in data
    assert "is_phishing" in data


def test_predict_phishing_url(client):
    r = client.post("/v1/predict", json={"url": "http://paypal.verify-secure-login.suspicious-domain.net/confirm/account"})
    assert r.status_code == 200
    data = r.get_json()
    assert "phishing_probability" in data
    assert data["phishing_probability"] > 0.1


def test_predict_returns_latency(client):
    r = client.post("/v1/predict", json={"url": "http://example.com"})
    assert r.status_code == 200
    data = r.get_json()
    assert "latency_ms" in data
    assert data["latency_ms"] >= 0


def test_predict_missing_url_field(client):
    r = client.post("/v1/predict", json={"website": "http://example.com"})
    assert r.status_code == 400


def test_predict_empty_url(client):
    r = client.post("/v1/predict", json={"url": ""})
    assert r.status_code == 400


def test_predict_url_without_scheme(client):
    r = client.post("/v1/predict", json={"url": "example.com"})
    assert r.status_code == 200
    data = r.get_json()
    assert "is_phishing" in data


def test_predict_returns_model_name(client):
    r = client.post("/v1/predict", json={"url": "http://example.com"})
    assert r.status_code == 200
    data = r.get_json()
    assert "model" in data


def test_health_returns_schema_version(client):
    r = client.get("/v1/health")
    assert r.status_code == 200
    data = r.get_json()
    assert "schema" in data