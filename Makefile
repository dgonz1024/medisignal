PYTHON := .venv/bin/python
UVICORN := .venv/bin/uvicorn

.PHONY: init-db ingest ingest-deep pipeline api dev

init-db:
	PYTHONPATH=. $(PYTHON) scripts/init_db.py

ingest:
	PYTHONPATH=. $(PYTHON) scripts/run_ingestion.py

ingest-deep:
	PYTHONPATH=. $(PYTHON) scripts/run_ingestion.py --max-pages 20 --page-size 100

pipeline:
	PYTHONPATH=. $(PYTHON) scripts/run_pipeline.py

api:
	PYTHONPATH=. $(UVICORN) app.main:app --host 127.0.0.1 --port 8000

dev:
	PYTHONPATH=. $(UVICORN) app.main:app --host 127.0.0.1 --port 8000 --reload
