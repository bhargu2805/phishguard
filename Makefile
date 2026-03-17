.PHONY: install dev test lint run train

install:
	python -m pip install -r requirements.txt

dev:
	python -m pip install -r requirements-dev.txt

test:
	pytest -q --disable-warnings --maxfail=1 --cov=phishguard --cov-report=term-missing

lint:
	ruff check .

run:
	PYTHONPATH=src python wsgi.py

train:
	PYTHONPATH=src python -m phishguard.train --csv data/urls.csv --out artifacts
