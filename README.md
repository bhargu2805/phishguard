# PhishGuard — Phishing Website Detection with Flask API (RandomForest + SMOTE)

A GitHub-ready, Master’s-level project that looks good on a resume:
- **Flask REST API** for real-time phishing detection
- **URL-based feature extraction** (no network calls; safe + fast)
- **Random Forest** classifier trained with **SMOTE** to handle class imbalance
- **Unit tests + API endpoint validation** with `pytest`
- **Docker + GitHub Actions CI**

## 1) Project structure

```
phishing-flask-api/
├─ src/phishguard/              # package (features, API, training)
├─ tests/                       # unit + API tests
├─ scripts/                     # dataset helper scripts
├─ artifacts/                   # trained model + metrics (generated)
├─ wsgi.py                      # app entrypoint
├─ Dockerfile / docker-compose.yml
└─ .github/workflows/ci.yml     # CI
```

## 2) Setup (local)

**Requirements**: Python 3.10+ recommended.

```bash
git clone <your-repo-url>
cd phishing-flask-api

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements-dev.txt
pip install -e .
```

## 3) Dataset (url,label)

This project trains from a CSV that contains **raw URLs**:

**`data/urls.csv`**
```csv
url,label
https://example.com,0
http://paypal.verify-secure-login.example.net/confirm,1
```

Create a starter template:
```bash
python scripts/make_url_dataset_template.py --out data/urls.csv
```

### Where to get URLs (recommended)
- **PhishTank**: phishing URLs export (label=1)
- **Tranco Top Sites** (or similar): legit domains/URLs (label=0)

> Note: The popular **UCI “Phishing Websites”** dataset is feature-engineered and typically **does not contain raw URLs**.
If you downloaded it as ARFF, you can convert it to a CSV of features using:
```bash
python scripts/uci_arff_to_csv.py --arff data/phishing.arff --out data/uci_phishing_features.csv
```
But for **URL-based** feature extraction, you want a dataset containing actual URLs.

## 4) Train the model (RandomForest + SMOTE)

```bash
PYTHONPATH=src python -m phishguard.train --csv data/urls.csv --out artifacts
```

Outputs:
- `artifacts/model.joblib` — model bundle
- `artifacts/metrics.json` — accuracy/recall/F1/AUC

### About the “+10% recall” bullet
If your dataset is imbalanced (realistic), SMOTE typically improves phishing-class recall.
Your exact gain depends on the dataset; the training script saves `metrics.json` so you can cite your measured improvement.

## 5) Run the API

```bash
PYTHONPATH=src python wsgi.py
```

Test:
```bash
curl http://localhost:5000/v1/health
```

Predict:
```bash
curl -X POST http://localhost:5000/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"url":"http://paypal.verify-secure-login.example.net/confirm"}'
```

Response:
```json
{
  "url": "...",
  "is_phishing": true,
  "phishing_probability": 0.9134,
  "model": "random_forest_smote",
  "model_version": "20260210123456",
  "latency_ms": 2
}
```

## 6) Run tests

```bash
pytest -q
```

## 7) Docker

```bash
docker compose up --build
```

Make sure you have a trained model at `./artifacts/model.joblib` (mounted into the container).

## 8) Resume bullets (copy/paste)

- Developed a back-end service using **Flask** to expose a **RESTful API** for real-time phishing website detection  
- Implemented data workflows to extract **URL-based features** and applied a **Random Forest** classifier for prediction  
- Applied **SMOTE** to handle class imbalance, improving phishing-class **recall** on the validation set (see `artifacts/metrics.json`)  
- Integrated **unit tests** and API endpoint validation with **pytest** and GitHub Actions CI to ensure reliability

## 9) Next upgrades (optional, looks great in interviews)
- Add a `/v1/batch_predict` endpoint for lists of URLs
- Add model monitoring: log latency + confidence + drift signals
- Add a lightweight UI page (Swagger/OpenAPI or simple HTML)
- Add feature importance endpoint for explainability
