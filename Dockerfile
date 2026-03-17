FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
COPY wsgi.py /app/wsgi.py
COPY pyproject.toml /app/pyproject.toml
COPY train_on_startup.py /app/train_on_startup.py

RUN pip install -e .

RUN python train_on_startup.py && \
    PYTHONPATH=src python -m phishguard.train --csv data/urls.csv --out artifacts

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--pythonpath", "src", "wsgi:app"]
