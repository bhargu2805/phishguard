#!/bin/bash
echo "Checking for trained model..."
if [ ! -f "artifacts/model.joblib" ]; then
    echo "Model not found. Downloading dataset and training..."
    mkdir -p data artifacts
    python3 -c "
from datasets import load_dataset
import pandas as pd
ds = load_dataset('pirocheto/phishing-url', split='train')
df = pd.DataFrame(ds)
df['label'] = (df['status'] == 'phishing').astype(int)
df[['url', 'label']].to_csv('data/urls.csv', index=False)
print('Dataset ready.')
"
    PYTHONPATH=src python -m phishguard.train --csv data/urls.csv --out artifacts
    echo "Model trained and ready."
fi
echo "Starting Flask API..."
PYTHONPATH=src gunicorn --bind 0.0.0.0:$PORT wsgi:app
