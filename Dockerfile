FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
COPY wsgi.py /app/wsgi.py
COPY pyproject.toml /app/pyproject.toml

RUN pip install -e .

# Download dataset and train model at build time
RUN mkdir -p data artifacts && \
    python3 -c "
from datasets import load_dataset
import pandas as pd
ds = load_dataset('pirocheto/phishing-url', split='train')
df = pd.DataFrame(ds)
df['label'] = (df['status'] == 'phishing').astype(int)
df[['url', 'label']].to_csv('data/urls.csv', index=False)
print('Dataset ready.')
" && \
    PYTHONPATH=src python -m phishguard.train --csv data/urls.csv --out artifacts

EXPOSE 5000

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--pythonpath", "src", "wsgi:app"]
