FROM python:3.11-slim

WORKDIR /app

# System deps (kept minimal)
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
COPY wsgi.py /app/wsgi.py
COPY pyproject.toml /app/pyproject.toml

# Default model path in container
ENV PHISHGUARD_MODEL_PATH=/app/artifacts/model.joblib
ENV PYTHONPATH=/app/src

EXPOSE 5000
CMD ["python", "wsgi.py"]
