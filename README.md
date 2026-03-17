# PhishGuard — Real-Time Phishing Website Detection API

A production-ready REST API for real-time phishing website detection using machine learning. Trained on 7,658 real labeled URLs, achieving **88.3% accuracy** and **94.9% ROC-AUC**. Containerized with Docker and deployed with GitHub Actions CI.

## Demo

```bash
curl -X POST https://phishguard.onrender.com/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal.verify-secure-login.suspicious-domain.net/confirm"}'
```

```json
{
  "is_phishing": true,
  "phishing_probability": 0.915,
  "model": "random_forest_smote",
  "latency_ms": 26
}
```

## Architecture

```
phishguard/
├── src/phishguard/
│   ├── app.py          # Flask app factory
│   ├── routes.py       # API endpoints (/health, /predict)
│   ├── features.py     # URL feature extraction (26 features)
│   ├── model.py        # Model loading and inference
│   └── train.py        # Training pipeline (Random Forest + SMOTE)
├── tests/
│   ├── test_api.py     # API endpoint tests (12 test cases)
│   └── test_features.py
├── artifacts/
│   └── metrics.json    # Real model performance metrics
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## How It Works

1. A URL is submitted to the `/predict` endpoint
2. 26 features are extracted from the URL — length, special characters, suspicious keywords, IP patterns, subdomain depth, digit ratios, and more
3. A trained Random Forest classifier predicts whether the URL is phishing or legitimate
4. The response includes the prediction, confidence score, and response latency

## Model Performance

Trained on the [Phishing URL dataset](https://huggingface.co/datasets/pirocheto/phishing-url) — 7,658 real labeled URLs (50/50 phishing vs legitimate split).

| Metric | Score |
|--------|-------|
| Accuracy | 88.3% |
| Recall (phishing) | 89.2% |
| Precision (phishing) | 87.7% |
| F1 Score | 88.4% |
| ROC-AUC | 94.9% |

SMOTE oversampling was applied during training to ensure balanced learning on the phishing class. Full metrics available in [`artifacts/metrics.json`](artifacts/metrics.json).

## Tech Stack

- **Backend**: Python, Flask, REST API
- **ML**: scikit-learn, Random Forest, SMOTE (imbalanced-learn)
- **Feature Engineering**: 26 URL-based features, no network calls required
- **Testing**: pytest — 12 test cases covering endpoints and feature extraction
- **DevOps**: Docker, docker-compose, GitHub Actions CI

## Setup (Local)

**Requirements**: Python 3.10+

```bash
git clone https://github.com/bhargu2805/phishguard.git
cd phishguard

python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux

pip install -r requirements-dev.txt
pip install -e .
```

## Train the Model

Download the dataset and train:

```bash
python3 -c "
from datasets import load_dataset
import pandas as pd
ds = load_dataset('pirocheto/phishing-url', split='train')
df = pd.DataFrame(ds)
df['label'] = (df['status'] == 'phishing').astype(int)
df[['url', 'label']].to_csv('data/urls.csv', index=False)
"

PYTHONPATH=src python -m phishguard.train --csv data/urls.csv --out artifacts
```

## Run the API

```bash
PYTHONPATH=src python -c "
from phishguard import create_app
app = create_app()
app.run(debug=True, port=8000)
"
```

## Run with Docker

```bash
docker compose up --build
```

API available at `http://localhost:5001`

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/v1/health
```
```json
{ "status": "ok", "schema": "v1" }
```

### Predict
```bash
curl -X POST http://localhost:8000/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```
```json
{
  "is_phishing": false,
  "phishing_probability": 0.01157,
  "model": "random_forest_smote",
  "latency_ms": 26
}
```

## Run Tests

```bash
pytest -q
```
```
12 passed in 0.08s
```

## CI/CD

GitHub Actions runs automatically on every push:
- Installs dependencies
- Runs `ruff` linter
- Runs full `pytest` suite

## Author

**Bhargavi Chowdary Chilukuri**  
MS Computer Science, University of Central Florida  
[LinkedIn](https://www.linkedin.com/in/bhargavi-chowdary-chilukuri-a3ba45225/) | [GitHub](https://github.com/bhargu2805)