from app.core.db import SessionLocal, initialize_database
from app.pipeline.analytics import persist_staging_record, refresh_aggregate_analytics
from app.pipeline.raw_loader import load_raw_records
from app.pipeline.normalize import normalize_study_record
from app.pipeline.validators import validate_study_record


def main() -> None:
    initialize_database()

    with SessionLocal() as session:
        records = load_raw_records(session=session)
        processed_count = 0
        quality_issue_count = 0

        for record in records:
            normalized = normalize_study_record(
                {
                    "nct_id": record.nct_id,
                    "payload_jsonb": record.payload_jsonb,
                }
            )
            issues = validate_study_record(normalized)
            persist_staging_record(session=session, normalized_record=normalized, issues=issues)
            processed_count += 1
            quality_issue_count += len(issues)

        refresh_aggregate_analytics(session=session)
        session.commit()

    print(
        {
            "processed_records": processed_count,
            "quality_issues_detected": quality_issue_count,
        }
    )


if __name__ == "__main__":
    main()
