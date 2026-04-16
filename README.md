# MediSignal

MediSignal is a clinical trial intelligence prototype built on top of public ClinicalTrials.gov data.

Today, the project does four real things:

- ingests live study records from the ClinicalTrials.gov API
- preserves the raw source payload in PostgreSQL
- normalizes records into structured tables for querying and analytics
- exposes the data through a FastAPI API and a browser-based research dashboard

The current product direction is moving toward a tool that helps research teams, clinics, and health-tech companies explore patterns across trials, sponsors, phases, conditions, and early termination behavior.

## MediSignal Console

The system dashboard provides a quick operational overview of the ingested clinical trial dataset, including key metrics such as trial 
volume, top conditions, and sponsor distribution.

<img width="1104" height="628" alt="Screenshot 2026-04-16 at 10 08 24 AM" src="https://github.com/user-attachments/assets/291bc391-b2cd-477c-ae4c-fb2707b832ab" />

## Trial Explorer

The Explorer allows users to filter and inspect trials using structured fields such as phase, sponsor, condition, and enrollment size. Selecting a trial surfaces normalized study details extracted from the ClinicalTrials.gov dataset.

<img width="1151" height="686" alt="Screenshot 2026-04-16 at 10 10 23 AM" src="https://github.com/user-attachments/assets/4e4c6c82-4617-47ca-baa3-289a981e9e13" />

## Research Briefs

Aggregated analytics summarize sponsor and condition activity across the dataset, highlighting completion rates, enrollment patterns, and sponsor mix.

<img width="1099" height="685" alt="Screenshot 2026-04-16 at 10 11 46 AM" src="https://github.com/user-attachments/assets/635f0450-0e2f-4bd2-909b-04341ea2dcf7" />

## Pattern Watch

The Pattern Watch dashboard surfaces higher-level signals such as early termination patterns and underrepresented research areas.

<img width="1094" height="567" alt="Screenshot 2026-04-16 at 10 12 07 AM" src="https://github.com/user-attachments/assets/c4870d65-319e-45a7-bd65-18729a5e5cf4" />

## What The Program Does Right Now

MediSignal currently supports:

- live ingestion of 10,000+ clinical trials from ClinicalTrials.gov v2
- multi-page ingestion for larger local datasets
- raw, staging, and analytics schemas in PostgreSQL
- ETL normalization from nested API JSON into relational tables
- basic data quality issue recording
- trial listing, detail, and quality endpoints
- analytics endpoints for sponsors, conditions, status buckets, termination patterns, and low-coverage conditions
- sponsor and condition drill-down analytics
- a browser dashboard with:
  - trial explorer
  - trial detail panel
  - research signal panels
  - sponsor and condition research briefs
  - autosuggest for searchable fields
  - clickable drill-downs from analytics into filtered trial results

## What It Is Useful For

The project is most useful right now for:

- exploring trial patterns in a local slice of ClinicalTrials.gov data
- comparing sponsor activity
- inspecting condition coverage
- looking at status mix and early termination patterns
- drilling from analytics summaries into matching trial lists

Examples of questions the current build can help answer:

- Which sponsors appear most active in this local dataset?
- Which conditions show low trial coverage?
- Which phases in this dataset show more early termination?
- What does a given sponsor's portfolio look like?
- What does the trial landscape for a specific condition look like?

## Current Architecture

```text
ClinicalTrials.gov API
        ->
Python ingestion service
        ->
raw.study_records
        ->
normalization and validation pipeline
        ->
staging tables
        ->
analytics tables
        ->
FastAPI API
        ->
interactive dashboard
```

## Database Design

MediSignal uses three PostgreSQL schemas:

- `raw`
  Preserves the original API payload for reproducibility and reprocessing.

- `staging`
  Stores flattened, source-aligned trial data such as studies, conditions, interventions, and locations.

- `analytics`
  Stores application-facing summaries and quality findings used by the API and dashboard.

This separation matters because each layer has a different job:

- raw keeps the source of truth
- staging makes the data easier to validate and query
- analytics makes it easier to answer higher-level questions quickly

## Main API Endpoints

### Health

- `GET /health`

### Trial Data

- `GET /trials`
- `GET /trials/{nct_id}`
- `GET /trials/{nct_id}/quality`

The `/trials` endpoint supports filtering, pagination, and sorting.  
It also supports grouped status filtering through `status_bucket` for values like:

- `active`
- `completed`
- `terminated_early`

### Analytics

- `GET /stats/conditions`
- `GET /stats/sponsors`
- `GET /stats/status-overview`
- `GET /stats/terminations/phases`
- `GET /stats/terminations/sponsors`
- `GET /stats/coverage/conditions`
- `GET /stats/sponsors/{sponsor_name}`
- `GET /stats/conditions/{condition_name}`
- `GET /stats/autocomplete`

### Scoring

- `POST /score/completion-risk`

The scoring module is still lightweight and intentionally simple.

## Dashboard

The browser dashboard is available at:

- `http://127.0.0.1:8000/`

The dashboard currently includes:

- overview cards
- trial explorer with filters, autosuggest, pagination, and page jump
- selected trial detail panel
- research signal panels
- sponsor research brief
- condition research brief
- drill-down behavior from analytics cards into matching trial sets

## Local Setup

### 1. Create the environment file

```bash
cd medisignal
cp .env.example .env
```

Make sure the database user in `.env` matches your local PostgreSQL setup.

### 2. Make sure PostgreSQL is running

On this machine the project has been run against a local PostgreSQL service.

### 3. Initialize the database

```bash
make init-db
```

### 4. Ingest data

Quick sample:

```bash
make ingest
```

Larger local dataset:

```bash
make ingest-deep
```

`make ingest` is useful for quick testing.  
`make ingest-deep` is much better for analytics because it pulls a broader dataset.

You can also control ingestion size directly:

```bash
PYTHONPATH=. .venv/bin/python scripts/run_ingestion.py --max-pages 20 --page-size 100
```

### 5. Run the pipeline

```bash
make pipeline
```

### 6. Start the API

```bash
make api
```

For auto-reload during development:

```bash
make dev
```

## Project Structure

```text
medisignal/
├── app/
│   ├── api/
│   ├── core/
│   ├── ingestion/
│   ├── models/
│   ├── pipeline/
│   ├── scoring/
│   └── main.py
├── migrations/
├── scripts/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
└── README.md
```

## Important Limitations

This README is intentionally based on what the program actually does today, so here are the main limitations:

- the dataset is only as broad as what has been ingested locally
- analytics are descriptive, not scientific conclusions
- "underrepresented" currently means low count in the ingested dataset, not a definitive statement about global research
- status bucketing is heuristic
- search and autosuggest are useful, but not yet a full ranked search engine
- data quality checks exist, but they are still relatively lightweight
- this is not a medical advice product

## Future Plans For The Project

The next major step for the project is making the product more clearly useful for real users by improving:

- condition intelligence
- sponsor benchmarking
- trend analysis
- search and ranking
- methodology transparency
