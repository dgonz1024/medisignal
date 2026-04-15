from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.tables import StudyRecord


def load_raw_records(session: Session, limit: int | None = None) -> list[StudyRecord]:
    statement = select(StudyRecord).order_by(
        StudyRecord.nct_id,
        desc(StudyRecord.fetched_at),
        desc(StudyRecord.id),
    )
    if limit is not None:
        statement = statement.limit(limit)

    records = session.execute(statement).scalars().all()

    latest_records_by_nct_id: dict[str, StudyRecord] = {}
    for record in records:
        if record.nct_id not in latest_records_by_nct_id:
            latest_records_by_nct_id[record.nct_id] = record

    return list(latest_records_by_nct_id.values())
