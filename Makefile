PYTHON := .venv/bin/python
UVICORN := .venv/bin/uvicorn

.PHONY: init-db ingest ingest-deep pipeline bootstrap-data api dev

init-db:
	PYTHONPATH=. $(PYTHON) scripts/init_db.py

ingest:
	PYTHONPATH=. $(PYTHON) scripts/run_ingestion.py

ingest-deep:
	PYTHONPATH=. $(PYTHON) scripts/run_ingestion.py --max-pages 120 --page-size 100

pipeline:
	PYTHONPATH=. $(PYTHON) scripts/run_pipeline.py

bootstrap-data:
	PYTHONPATH=. $(PYTHON) scripts/bootstrap_data.py

api:
	PYTHONPATH=. $(UVICORN) app.main:app --host 127.0.0.1 --port 8000

dev:
	PYTHONPATH=. $(UVICORN) app.main:app --host 127.0.0.1 --port 8000 --reload
