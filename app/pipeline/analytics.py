from datetime import datetime, timezone
from typing import Any

from sqlalchemy import case, delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.tables import (
    ConditionStats,
    QualityIssue,
    StagingCondition,
    StagingIntervention,
    StagingLocation,
    StagingStudy,
    SponsorStats,
    TrialSummary,
)


def build_trial_summary(study: dict[str, Any], condition_count: int, location_count: int) -> dict[str, Any]:
    sponsor_name = study.get("sponsor_name") or ""
    sponsor_type = "Industry" if any(
        keyword in sponsor_name.lower() for keyword in ("inc", "corp", "corporation", "ltd", "llc", "gmbh")
    ) else "Other"

    return {
        "nct_id": study.get("nct_id"),
        "phase": study.get("phase"),
        "status": study.get("overall_status"),
        "enrollment_count": study.get("enrollment_count"),
        "location_count": location_count,
        "condition_count": condition_count,
        "sponsor_type": sponsor_type,
    }


def persist_staging_record(session: Session, normalized_record: dict[str, Any], issues: list[dict[str, str]]) -> None:
    study = normalized_record["study"]
    nct_id = study["nct_id"]

    if not nct_id:
        return

    session.execute(
        insert(StagingStudy)
        .values(study)
        .on_conflict_do_update(
            index_elements=[StagingStudy.nct_id],
            set_={key: value for key, value in study.items() if key != "nct_id"},
        )
    )

    session.execute(delete(StagingCondition).where(StagingCondition.nct_id == nct_id))
    session.execute(delete(StagingIntervention).where(StagingIntervention.nct_id == nct_id))
    session.execute(delete(StagingLocation).where(StagingLocation.nct_id == nct_id))
    session.execute(delete(QualityIssue).where(QualityIssue.nct_id == nct_id))

    if normalized_record["conditions"]:
        session.execute(insert(StagingCondition), normalized_record["conditions"])

    if normalized_record["interventions"]:
        session.execute(insert(StagingIntervention), normalized_record["interventions"])

    if normalized_record["locations"]:
        session.execute(insert(StagingLocation), normalized_record["locations"])

    if issues:
        issue_rows = [
            {
                "nct_id": nct_id,
                "issue_type": issue["issue_type"],
                "issue_description": issue["issue_description"],
                "detected_at": datetime.now(timezone.utc),
            }
            for issue in issues
        ]
        session.execute(insert(QualityIssue), issue_rows)

    trial_summary = build_trial_summary(
        study=study,
        condition_count=len(normalized_record["conditions"]),
        location_count=len(normalized_record["locations"]),
    )
    session.execute(
        insert(TrialSummary)
        .values(trial_summary)
        .on_conflict_do_update(
            index_elements=[TrialSummary.nct_id],
            set_={key: value for key, value in trial_summary.items() if key != "nct_id"},
        )
    )


def refresh_aggregate_analytics(session: Session) -> None:
    session.execute(delete(ConditionStats))
    session.execute(delete(SponsorStats))

    condition_rows = session.execute(
        select(
            StagingCondition.condition_name,
            func.count(func.distinct(StagingCondition.nct_id)).label("trial_count"),
            func.avg(StagingStudy.enrollment_count).label("avg_enrollment"),
        )
        .join(StagingStudy, StagingStudy.nct_id == StagingCondition.nct_id)
        .group_by(StagingCondition.condition_name)
    ).all()

    if condition_rows:
        session.execute(
            insert(ConditionStats),
            [
                {
                    "condition_name": condition_name,
                    "trial_count": trial_count,
                    "avg_enrollment": avg_enrollment,
                }
                for condition_name, trial_count, avg_enrollment in condition_rows
            ],
        )

    completed_statuses = ("completed", "active, not recruiting", "approved for marketing")
    sponsor_rows = session.execute(
        select(
            StagingStudy.sponsor_name,
            func.count(StagingStudy.nct_id).label("trial_count"),
            (
                func.sum(
                    case(
                        (
                            func.lower(StagingStudy.overall_status).in_(completed_statuses),
                            1,
                        ),
                        else_=0,
                    )
                )
                / func.nullif(func.count(StagingStudy.nct_id), 0)
            ).label("completion_rate"),
        )
        .where(StagingStudy.sponsor_name.is_not(None))
        .group_by(StagingStudy.sponsor_name)
    ).all()

    if sponsor_rows:
        session.execute(
            insert(SponsorStats),
            [
                {
                    "sponsor_name": sponsor_name,
                    "trial_count": trial_count,
                    "completion_rate": completion_rate,
                }
                for sponsor_name, trial_count, completion_rate in sponsor_rows
                if sponsor_name
            ],
        )
