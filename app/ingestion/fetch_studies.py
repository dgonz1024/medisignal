import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.ingestion.client import ClinicalTrialsClient
from app.ingestion.pagination import build_page_params
from app.models.tables import StudyRecord

logger = logging.getLogger(__name__)


def fetch_study_batch(page_token: str | None = None, page_size: int = 100) -> dict:
    client = ClinicalTrialsClient()
    params = build_page_params(page_token=page_token, page_size=page_size)
    logger.info("Fetching studies from ClinicalTrials.gov")
    return client.fetch_studies(params=params)


def extract_studies_from_response(payload: dict[str, Any]) -> list[dict[str, Any]]:
    studies = payload.get("studies")
    if isinstance(studies, list):
        return studies

    full_studies = payload.get("FullStudiesResponse", {}).get("FullStudies")
    if isinstance(full_studies, list):
        extracted_studies: list[dict[str, Any]] = []
        for item in full_studies:
            if isinstance(item, dict):
                study_payload = item.get("Study", item)
                if isinstance(study_payload, dict):
                    extracted_studies.append(study_payload)
        return extracted_studies

    return []


def extract_next_page_token(payload: dict[str, Any]) -> str | None:
    next_page_token = payload.get("nextPageToken")
    if isinstance(next_page_token, str) and next_page_token:
        return next_page_token

    next_page_token = payload.get("NextPageToken")
    if isinstance(next_page_token, str) and next_page_token:
        return next_page_token

    return None


def extract_nct_id(study_payload: dict[str, Any]) -> str | None:
    direct_nct_id = study_payload.get("nctId")
    if isinstance(direct_nct_id, str) and direct_nct_id:
        return direct_nct_id

    direct_nct_id = study_payload.get("NCTId")
    if isinstance(direct_nct_id, str) and direct_nct_id:
        return direct_nct_id

    protocol_section = study_payload.get("protocolSection", {})
    identification_module = protocol_section.get("identificationModule", {})
    nested_nct_id = identification_module.get("nctId")
    if isinstance(nested_nct_id, str) and nested_nct_id:
        return nested_nct_id

    study_info = study_payload.get("Study", {}).get("ProtocolSection", {}).get("IdentificationModule", {})
    nested_nct_id = study_info.get("NCTId")
    if isinstance(nested_nct_id, str) and nested_nct_id:
        return nested_nct_id

    return None


def build_source_hash(study_payload: dict[str, Any]) -> str:
    canonical_payload = json.dumps(study_payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()


def store_raw_study_records(session: Session, studies: list[dict[str, Any]]) -> dict[str, int]:
    fetched_at = datetime.now(timezone.utc)
    rows_to_insert: list[dict[str, Any]] = []
    skipped_missing_nct_id = 0

    for study_payload in studies:
        nct_id = extract_nct_id(study_payload)
        if not nct_id:
            skipped_missing_nct_id += 1
            continue

        rows_to_insert.append(
            {
                "nct_id": nct_id,
                "fetched_at": fetched_at,
                "source_hash": build_source_hash(study_payload),
                "payload_jsonb": study_payload,
            }
        )

    if not rows_to_insert:
        return {
            "inserted": 0,
            "duplicates_skipped": 0,
            "missing_nct_id_skipped": skipped_missing_nct_id,
        }

    statement = insert(StudyRecord).values(rows_to_insert)
    statement = statement.on_conflict_do_nothing(
        constraint="uq_raw_study_records_nct_id_source_hash"
    ).returning(StudyRecord.nct_id)
    result = session.execute(statement)
    session.commit()

    inserted_count = len(result.scalars().all())
    duplicate_count = len(rows_to_insert) - inserted_count

    return {
        "inserted": inserted_count,
        "duplicates_skipped": duplicate_count,
        "missing_nct_id_skipped": skipped_missing_nct_id,
    }


def ingest_study_batch(
    session: Session,
    page_token: str | None = None,
    page_size: int = 100,
) -> dict[str, Any]:
    response_payload = fetch_study_batch(page_token=page_token, page_size=page_size)
    studies = extract_studies_from_response(response_payload)
    storage_summary = store_raw_study_records(session=session, studies=studies)

    return {
        "fetched_count": len(studies),
        "next_page_token": extract_next_page_token(response_payload),
        **storage_summary,
    }


def ingest_study_pages(
    session: Session,
    max_pages: int = 5,
    page_size: int = 100,
) -> dict[str, Any]:
    totals = {
        "pages_processed": 0,
        "fetched_count": 0,
        "inserted": 0,
        "duplicates_skipped": 0,
        "missing_nct_id_skipped": 0,
    }
    page_token: str | None = None
    last_page_summary: dict[str, Any] | None = None

    for _ in range(max_pages):
        page_summary = ingest_study_batch(
            session=session,
            page_token=page_token,
            page_size=page_size,
        )
        last_page_summary = page_summary

        totals["pages_processed"] += 1
        totals["fetched_count"] += page_summary["fetched_count"]
        totals["inserted"] += page_summary["inserted"]
        totals["duplicates_skipped"] += page_summary["duplicates_skipped"]
        totals["missing_nct_id_skipped"] += page_summary["missing_nct_id_skipped"]

        page_token = page_summary.get("next_page_token")
        if not page_token:
            break

    return {
        **totals,
        "next_page_token": page_token,
        "completed_all_available_pages": bool(last_page_summary) and not page_token,
    }
