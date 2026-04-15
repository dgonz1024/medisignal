from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.api.schemas import (
    AutocompleteResponse,
    ConditionCoverageResponse,
    ConditionDetailResponse,
    ConditionStatsResponse,
    SponsorDetailResponse,
    SponsorStatsResponse,
    StatusCountItem,
    StatusOverviewResponse,
    TerminationStatsResponse,
)
from app.core.db import get_db_session
from app.models.tables import SponsorStats, StagingCondition, StagingStudy, TrialSummary

router = APIRouter(prefix="/stats", tags=["stats"])


def _status_bucket_expression():
    normalized_status = func.lower(func.coalesce(TrialSummary.status, ""))
    return case(
        (
            normalized_status.in_(
                [
                    "terminated",
                    "withdrawn",
                    "suspended",
                ]
            ),
            "terminated_early",
        ),
        (
            normalized_status.in_(
                [
                    "completed",
                    "approved for marketing",
                ]
            ),
            "completed",
        ),
        (
            normalized_status.in_(
                [
                    "recruiting",
                    "active_not_recruiting",
                    "enrolling_by_invitation",
                    "not_yet_recruiting",
                ]
            ),
            "active",
        ),
        (
            normalized_status.in_(
                [
                    "unknown",
                    "withheld",
                    "no_longer_available",
                    "temporarily_not_available",
                ]
            ),
            "unknown_or_unavailable",
        ),
        else_="other",
    )


def _terminated_early_flag():
    return case(
        (_status_bucket_expression() == "terminated_early", 1),
        else_=0,
    )


@router.get("/conditions", response_model=ConditionStatsResponse)
def get_condition_stats(
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> ConditionStatsResponse:
    statement = (
        select(
            StagingCondition.condition_name,
            func.count(func.distinct(StagingCondition.nct_id)).label("trial_count"),
            func.avg(StagingStudy.enrollment_count).label("avg_enrollment"),
        )
        .join(StagingStudy, StagingStudy.nct_id == StagingCondition.nct_id)
        .group_by(StagingCondition.condition_name)
        .order_by(func.count(func.distinct(StagingCondition.nct_id)).desc(), StagingCondition.condition_name)
        .limit(limit)
    )
    rows = db.execute(statement).all()

    return ConditionStatsResponse(
        count=len(rows),
        results=[
            {
                "condition_name": condition_name,
                "trial_count": trial_count,
                "avg_enrollment": round(float(avg_enrollment), 2) if avg_enrollment is not None else None,
            }
            for condition_name, trial_count, avg_enrollment in rows
        ],
    )


@router.get("/sponsors", response_model=SponsorStatsResponse)
def get_sponsor_stats(
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> SponsorStatsResponse:
    rows = db.execute(
        select(SponsorStats).order_by(SponsorStats.trial_count.desc(), SponsorStats.sponsor_name).limit(limit)
    ).scalars().all()

    return SponsorStatsResponse(
        count=len(rows),
        results=[
            {
                "sponsor_name": row.sponsor_name,
                "trial_count": row.trial_count,
                "completion_rate": float(row.completion_rate) if row.completion_rate is not None else None,
            }
            for row in rows
        ],
    )


@router.get("/autocomplete", response_model=AutocompleteResponse)
def get_autocomplete_suggestions(
    field: str = Query(pattern="^(sponsor|condition|country|phase)$"),
    q: str = Query(default="", max_length=100),
    limit: int = Query(default=8, ge=1, le=25),
    db: Session = Depends(get_db_session),
) -> AutocompleteResponse:
    normalized_query = q.strip()

    if field == "sponsor":
        label = func.coalesce(StagingStudy.sponsor_name, "").label("label")
        statement = (
            select(
                label,
                func.count(StagingStudy.nct_id).label("usage_count"),
            )
            .where(StagingStudy.sponsor_name.is_not(None), StagingStudy.sponsor_name != "")
            .group_by(label)
        )
    elif field == "condition":
        label = func.coalesce(StagingCondition.condition_name, "").label("label")
        statement = (
            select(
                label,
                func.count(func.distinct(StagingCondition.nct_id)).label("usage_count"),
            )
            .where(StagingCondition.condition_name.is_not(None), StagingCondition.condition_name != "")
            .group_by(label)
        )
    elif field == "country":
        from app.models.tables import StagingLocation

        label = func.coalesce(StagingLocation.country, "").label("label")
        statement = (
            select(
                label,
                func.count(func.distinct(StagingLocation.nct_id)).label("usage_count"),
            )
            .where(StagingLocation.country.is_not(None), StagingLocation.country != "")
            .group_by(label)
        )
    else:
        label = func.coalesce(TrialSummary.phase, "Unspecified").label("label")
        statement = (
            select(
                label,
                func.count(TrialSummary.nct_id).label("usage_count"),
            )
            .group_by(label)
        )

    if normalized_query:
        statement = statement.where(label.ilike(f"%{normalized_query}%"))

    rows = db.execute(
        statement.order_by(func.count().desc(), label).limit(limit)
    ).all()

    suggestions = [value for value, _ in rows if value]
    return AutocompleteResponse(
        field=field,
        query=normalized_query,
        count=len(suggestions),
        suggestions=suggestions,
    )


@router.get("/status-overview", response_model=StatusOverviewResponse)
def get_status_overview(db: Session = Depends(get_db_session)) -> StatusOverviewResponse:
    status_bucket = _status_bucket_expression().label("status_bucket")
    bucket_rows = db.execute(
        select(
            status_bucket,
            func.count(TrialSummary.nct_id).label("trial_count"),
        )
        .group_by(status_bucket)
        .order_by(func.count(TrialSummary.nct_id).desc(), status_bucket)
    ).all()

    total_trials = sum(trial_count for _, trial_count in bucket_rows)
    terminated_early_trials = sum(
        trial_count for bucket_name, trial_count in bucket_rows if bucket_name == "terminated_early"
    )
    terminated_early_rate = round(
        terminated_early_trials / total_trials, 4
    ) if total_trials else 0.0

    return StatusOverviewResponse(
        total_trials=total_trials,
        terminated_early_trials=terminated_early_trials,
        terminated_early_rate=terminated_early_rate,
        buckets=[
            {
                "status_bucket": bucket_name,
                "trial_count": trial_count,
                "share_of_trials": round(trial_count / total_trials, 4) if total_trials else 0.0,
            }
            for bucket_name, trial_count in bucket_rows
        ],
    )


@router.get("/terminations/phases", response_model=TerminationStatsResponse)
def get_phase_termination_stats(
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> TerminationStatsResponse:
    terminated_early_flag = _terminated_early_flag()
    rows = db.execute(
        select(
            func.coalesce(TrialSummary.phase, "Unspecified").label("group_name"),
            func.count(TrialSummary.nct_id).label("trial_count"),
            func.sum(terminated_early_flag).label("terminated_early_count"),
            (
                func.sum(terminated_early_flag) / func.nullif(func.count(TrialSummary.nct_id), 0)
            ).label("terminated_early_rate"),
        )
        .group_by(func.coalesce(TrialSummary.phase, "Unspecified"))
        .order_by(
            (func.sum(terminated_early_flag) / func.nullif(func.count(TrialSummary.nct_id), 0)).desc(),
            func.count(TrialSummary.nct_id).desc(),
            func.coalesce(TrialSummary.phase, "Unspecified"),
        )
        .limit(limit)
    ).all()

    return TerminationStatsResponse(
        count=len(rows),
        results=[
            {
                "group_name": group_name,
                "trial_count": trial_count,
                "terminated_early_count": int(terminated_early_count or 0),
                "terminated_early_rate": round(float(terminated_early_rate or 0.0), 4),
            }
            for group_name, trial_count, terminated_early_count, terminated_early_rate in rows
        ],
    )


@router.get("/terminations/sponsors", response_model=TerminationStatsResponse)
def get_sponsor_termination_stats(
    limit: int = Query(default=25, ge=1, le=100),
    min_trials: int = Query(default=1, ge=1),
    db: Session = Depends(get_db_session),
) -> TerminationStatsResponse:
    terminated_early_flag = _terminated_early_flag()
    sponsor_name = func.coalesce(StagingStudy.sponsor_name, "Unknown Sponsor")
    rows = db.execute(
        select(
            sponsor_name.label("group_name"),
            func.count(TrialSummary.nct_id).label("trial_count"),
            func.sum(terminated_early_flag).label("terminated_early_count"),
            (
                func.sum(terminated_early_flag) / func.nullif(func.count(TrialSummary.nct_id), 0)
            ).label("terminated_early_rate"),
        )
        .join(StagingStudy, StagingStudy.nct_id == TrialSummary.nct_id)
        .group_by(sponsor_name)
        .having(func.count(TrialSummary.nct_id) >= min_trials)
        .order_by(
            (func.sum(terminated_early_flag) / func.nullif(func.count(TrialSummary.nct_id), 0)).desc(),
            func.count(TrialSummary.nct_id).desc(),
            sponsor_name,
        )
        .limit(limit)
    ).all()

    return TerminationStatsResponse(
        count=len(rows),
        results=[
            {
                "group_name": group_name,
                "trial_count": trial_count,
                "terminated_early_count": int(terminated_early_count or 0),
                "terminated_early_rate": round(float(terminated_early_rate or 0.0), 4),
            }
            for group_name, trial_count, terminated_early_count, terminated_early_rate in rows
        ],
    )


@router.get("/coverage/conditions", response_model=ConditionCoverageResponse)
def get_condition_coverage(
    limit: int = Query(default=25, ge=1, le=100),
    low_coverage_threshold: int = Query(default=2, ge=1, le=20),
    db: Session = Depends(get_db_session),
) -> ConditionCoverageResponse:
    rows = db.execute(
        select(
            StagingCondition.condition_name,
            func.count(func.distinct(StagingCondition.nct_id)).label("trial_count"),
        )
        .group_by(StagingCondition.condition_name)
        .order_by(func.count(func.distinct(StagingCondition.nct_id)).asc(), StagingCondition.condition_name)
        .limit(limit)
    ).all()

    return ConditionCoverageResponse(
        count=len(rows),
        low_coverage_threshold=low_coverage_threshold,
        results=[
            {
                "condition_name": condition_name,
                "trial_count": trial_count,
                "coverage_label": "underrepresented" if trial_count <= low_coverage_threshold else "established",
            }
            for condition_name, trial_count in rows
        ],
    )


@router.get("/sponsors/{sponsor_name}", response_model=SponsorDetailResponse)
def get_sponsor_detail(sponsor_name: str, db: Session = Depends(get_db_session)) -> SponsorDetailResponse:
    terminated_early_flag = _terminated_early_flag()

    summary_row = db.execute(
        select(
            func.count(TrialSummary.nct_id).label("trial_count"),
            func.avg(TrialSummary.enrollment_count).label("average_enrollment"),
            func.sum(terminated_early_flag).label("terminated_early_count"),
            (
                func.sum(terminated_early_flag) / func.nullif(func.count(TrialSummary.nct_id), 0)
            ).label("terminated_early_rate"),
            (
                func.sum(
                    case(
                        (_status_bucket_expression() == "completed", 1),
                        else_=0,
                    )
                )
                / func.nullif(func.count(TrialSummary.nct_id), 0)
            ).label("completion_rate"),
        )
        .select_from(TrialSummary)
        .join(StagingStudy, StagingStudy.nct_id == TrialSummary.nct_id)
        .where(StagingStudy.sponsor_name == sponsor_name)
    ).one()

    trial_count = int(summary_row.trial_count or 0)
    if trial_count == 0:
        raise HTTPException(status_code=404, detail=f"Sponsor {sponsor_name} not found")

    phase_label = func.coalesce(TrialSummary.phase, "Unspecified").label("label")
    phase_rows = db.execute(
        select(
            phase_label,
            func.count(TrialSummary.nct_id).label("trial_count"),
        )
        .select_from(TrialSummary)
        .join(StagingStudy, StagingStudy.nct_id == TrialSummary.nct_id)
        .where(StagingStudy.sponsor_name == sponsor_name)
        .group_by(phase_label)
        .order_by(func.count(TrialSummary.nct_id).desc(), phase_label)
    ).all()

    status_label = func.coalesce(TrialSummary.status, "Unspecified").label("label")
    status_rows = db.execute(
        select(
            status_label,
            func.count(TrialSummary.nct_id).label("trial_count"),
        )
        .select_from(TrialSummary)
        .join(StagingStudy, StagingStudy.nct_id == TrialSummary.nct_id)
        .where(StagingStudy.sponsor_name == sponsor_name)
        .group_by(status_label)
        .order_by(func.count(TrialSummary.nct_id).desc(), status_label)
    ).all()

    condition_rows = db.execute(
        select(
            StagingCondition.condition_name.label("label"),
            func.count(func.distinct(StagingCondition.nct_id)).label("trial_count"),
        )
        .select_from(StagingCondition)
        .join(StagingStudy, StagingStudy.nct_id == StagingCondition.nct_id)
        .where(StagingStudy.sponsor_name == sponsor_name)
        .group_by(StagingCondition.condition_name)
        .order_by(func.count(func.distinct(StagingCondition.nct_id)).desc(), StagingCondition.condition_name)
        .limit(10)
    ).all()

    return SponsorDetailResponse(
        sponsor_name=sponsor_name,
        trial_count=trial_count,
        completion_rate=round(float(summary_row.completion_rate or 0.0), 4),
        terminated_early_count=int(summary_row.terminated_early_count or 0),
        terminated_early_rate=round(float(summary_row.terminated_early_rate or 0.0), 4),
        average_enrollment=round(float(summary_row.average_enrollment), 2) if summary_row.average_enrollment is not None else None,
        phase_distribution=[StatusCountItem(label=label, trial_count=trial_count) for label, trial_count in phase_rows],
        status_distribution=[StatusCountItem(label=label, trial_count=trial_count) for label, trial_count in status_rows],
        top_conditions=[StatusCountItem(label=label, trial_count=trial_count) for label, trial_count in condition_rows],
    )


@router.get("/conditions/{condition_name}", response_model=ConditionDetailResponse)
def get_condition_detail(condition_name: str, db: Session = Depends(get_db_session)) -> ConditionDetailResponse:
    terminated_early_flag = _terminated_early_flag()
    status_bucket = _status_bucket_expression()

    summary_row = db.execute(
        select(
            func.count(func.distinct(StagingCondition.nct_id)).label("trial_count"),
            func.avg(TrialSummary.enrollment_count).label("average_enrollment"),
            func.sum(terminated_early_flag).label("terminated_early_count"),
            (
                func.sum(terminated_early_flag) / func.nullif(func.count(TrialSummary.nct_id), 0)
            ).label("terminated_early_rate"),
            func.sum(
                case((status_bucket == "active", 1), else_=0)
            ).label("recruiting_count"),
            func.sum(
                case((status_bucket == "completed", 1), else_=0)
            ).label("completed_count"),
        )
        .select_from(StagingCondition)
        .join(TrialSummary, TrialSummary.nct_id == StagingCondition.nct_id)
        .where(StagingCondition.condition_name == condition_name)
    ).one()

    trial_count = int(summary_row.trial_count or 0)
    if trial_count == 0:
        raise HTTPException(status_code=404, detail=f"Condition {condition_name} not found")

    phase_label = func.coalesce(TrialSummary.phase, "Unspecified").label("label")
    phase_rows = db.execute(
        select(
            phase_label,
            func.count(func.distinct(StagingCondition.nct_id)).label("trial_count"),
        )
        .select_from(StagingCondition)
        .join(TrialSummary, TrialSummary.nct_id == StagingCondition.nct_id)
        .where(StagingCondition.condition_name == condition_name)
        .group_by(phase_label)
        .order_by(func.count(func.distinct(StagingCondition.nct_id)).desc(), phase_label)
    ).all()

    status_label = func.coalesce(TrialSummary.status, "Unspecified").label("label")
    status_rows = db.execute(
        select(
            status_label,
            func.count(func.distinct(StagingCondition.nct_id)).label("trial_count"),
        )
        .select_from(StagingCondition)
        .join(TrialSummary, TrialSummary.nct_id == StagingCondition.nct_id)
        .where(StagingCondition.condition_name == condition_name)
        .group_by(status_label)
        .order_by(func.count(func.distinct(StagingCondition.nct_id)).desc(), status_label)
    ).all()

    sponsor_type_label = func.coalesce(TrialSummary.sponsor_type, "Unknown").label("label")
    sponsor_type_rows = db.execute(
        select(
            sponsor_type_label,
            func.count(func.distinct(StagingCondition.nct_id)).label("trial_count"),
        )
        .select_from(StagingCondition)
        .join(TrialSummary, TrialSummary.nct_id == StagingCondition.nct_id)
        .where(StagingCondition.condition_name == condition_name)
        .group_by(sponsor_type_label)
        .order_by(func.count(func.distinct(StagingCondition.nct_id)).desc(), sponsor_type_label)
    ).all()

    return ConditionDetailResponse(
        condition_name=condition_name,
        trial_count=trial_count,
        recruiting_count=int(summary_row.recruiting_count or 0),
        completed_count=int(summary_row.completed_count or 0),
        terminated_early_count=int(summary_row.terminated_early_count or 0),
        terminated_early_rate=round(float(summary_row.terminated_early_rate or 0.0), 4),
        average_enrollment=round(float(summary_row.average_enrollment), 2) if summary_row.average_enrollment is not None else None,
        sponsor_type_distribution=[StatusCountItem(label=label, trial_count=trial_count) for label, trial_count in sponsor_type_rows],
        phase_distribution=[StatusCountItem(label=label, trial_count=trial_count) for label, trial_count in phase_rows],
        status_distribution=[StatusCountItem(label=label, trial_count=trial_count) for label, trial_count in status_rows],
    )
