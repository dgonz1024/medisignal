from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select, asc, case, desc, exists, func, select
from sqlalchemy.orm import Session

from app.api.schemas import TrialDetailResponse, TrialListItem, TrialListResponse, TrialQualityResponse
from app.core.db import get_db_session
from app.models.tables import (
    QualityIssue,
    StagingCondition,
    StagingIntervention,
    StagingLocation,
    StagingStudy,
    TrialSummary,
)

router = APIRouter(prefix="/trials", tags=["trials"])


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


def _apply_trial_filters(
    statement: Select,
    condition: str | None,
    phase: str | None,
    status: str | None,
    status_bucket: str | None,
    sponsor: str | None,
    sponsor_type: str | None,
    study_type: str | None,
    country: str | None,
    healthy_volunteers: bool | None,
    min_enrollment: int | None,
    max_enrollment: int | None,
) -> Select:
    bucket_expression = _status_bucket_expression()
    if phase:
        if phase == "Unspecified":
            statement = statement.where(TrialSummary.phase.is_(None))
        else:
            statement = statement.where(TrialSummary.phase == phase)
    if status:
        statement = statement.where(TrialSummary.status == status)
    if status_bucket:
        statement = statement.where(bucket_expression == status_bucket)
    if sponsor:
        statement = statement.where(StagingStudy.sponsor_name.ilike(f"%{sponsor}%"))
    if sponsor_type:
        statement = statement.where(TrialSummary.sponsor_type == sponsor_type)
    if study_type:
        statement = statement.where(StagingStudy.study_type == study_type)
    if country:
        statement = statement.where(
            exists(
                select(StagingLocation.id).where(
                    StagingLocation.nct_id == TrialSummary.nct_id,
                    StagingLocation.country.ilike(f"%{country}%"),
                )
            )
        )
    if healthy_volunteers is not None:
        statement = statement.where(StagingStudy.healthy_volunteers == healthy_volunteers)
    if min_enrollment is not None:
        statement = statement.where(TrialSummary.enrollment_count.is_not(None))
        statement = statement.where(TrialSummary.enrollment_count >= min_enrollment)
    if max_enrollment is not None:
        statement = statement.where(TrialSummary.enrollment_count.is_not(None))
        statement = statement.where(TrialSummary.enrollment_count <= max_enrollment)
    if condition:
        statement = statement.where(
            exists(
                select(StagingCondition.id).where(
                    StagingCondition.nct_id == TrialSummary.nct_id,
                    StagingCondition.condition_name.ilike(f"%{condition}%"),
                )
            )
        )
    return statement


def _apply_trial_sort(statement: Select, sort_by: str, sort_order: str) -> Select:
    sort_column_map = {
        "last_update_posted": StagingStudy.last_update_posted,
        "brief_title": StagingStudy.brief_title,
        "phase": TrialSummary.phase,
        "status": TrialSummary.status,
        "enrollment_count": TrialSummary.enrollment_count,
        "location_count": TrialSummary.location_count,
        "condition_count": TrialSummary.condition_count,
        "sponsor_name": StagingStudy.sponsor_name,
        "nct_id": TrialSummary.nct_id,
    }
    sort_column = sort_column_map[sort_by]
    sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)

    if sort_by in {"last_update_posted", "enrollment_count", "location_count", "condition_count"}:
        sort_expression = sort_expression.nullslast()

    return statement.order_by(sort_expression, TrialSummary.nct_id)


@router.get("", response_model=TrialListResponse)
def list_trials(
    condition: str | None = None,
    phase: str | None = None,
    status: str | None = None,
    status_bucket: str | None = Query(default=None, pattern="^(active|completed|terminated_early|unknown_or_unavailable|other)$"),
    sponsor: str | None = None,
    sponsor_type: str | None = Query(default=None, pattern="^(Industry|Other)$"),
    study_type: str | None = None,
    country: str | None = None,
    healthy_volunteers: bool | None = None,
    min_enrollment: int | None = Query(default=None, ge=0),
    max_enrollment: int | None = Query(default=None, ge=0),
    sort_by: str = Query(
        default="last_update_posted",
        pattern="^(last_update_posted|brief_title|phase|status|enrollment_count|location_count|condition_count|sponsor_name|nct_id)$",
    ),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> TrialListResponse:
    if min_enrollment is not None and max_enrollment is not None and min_enrollment > max_enrollment:
        raise HTTPException(status_code=400, detail="min_enrollment cannot be greater than max_enrollment")

    statement: Select[tuple[TrialSummary, StagingStudy]] = (
        select(TrialSummary, StagingStudy)
        .join(StagingStudy, StagingStudy.nct_id == TrialSummary.nct_id)
    )
    statement = _apply_trial_filters(
        statement=statement,
        condition=condition,
        phase=phase,
        status=status,
        status_bucket=status_bucket,
        sponsor=sponsor,
        sponsor_type=sponsor_type,
        study_type=study_type,
        country=country,
        healthy_volunteers=healthy_volunteers,
        min_enrollment=min_enrollment,
        max_enrollment=max_enrollment,
    )
    statement = _apply_trial_sort(statement=statement, sort_by=sort_by, sort_order=sort_order)

    count_statement = (
        select(func.count())
        .select_from(TrialSummary)
        .join(StagingStudy, StagingStudy.nct_id == TrialSummary.nct_id)
    )
    count_statement = _apply_trial_filters(
        statement=count_statement,
        condition=condition,
        phase=phase,
        status=status,
        status_bucket=status_bucket,
        sponsor=sponsor,
        sponsor_type=sponsor_type,
        study_type=study_type,
        country=country,
        healthy_volunteers=healthy_volunteers,
        min_enrollment=min_enrollment,
        max_enrollment=max_enrollment,
    )

    total = db.execute(count_statement).scalar_one()
    rows = db.execute(statement.limit(limit).offset(offset)).all()

    return TrialListResponse(
        total=total,
        limit=limit,
        offset=offset,
        results=[
            TrialListItem(
                nct_id=summary.nct_id,
                brief_title=study.brief_title,
                phase=summary.phase,
                status=summary.status,
                enrollment_count=summary.enrollment_count,
                location_count=summary.location_count,
                condition_count=summary.condition_count,
                sponsor_name=study.sponsor_name,
                sponsor_type=summary.sponsor_type,
            )
            for summary, study in rows
        ],
    )


@router.get("/{nct_id}", response_model=TrialDetailResponse)
def get_trial(nct_id: str, db: Session = Depends(get_db_session)) -> TrialDetailResponse:
    study = db.get(StagingStudy, nct_id)
    if study is None:
        raise HTTPException(status_code=404, detail=f"Trial {nct_id} not found")

    summary = db.get(TrialSummary, nct_id)
    conditions = db.execute(
        select(StagingCondition.condition_name).where(StagingCondition.nct_id == nct_id).order_by(StagingCondition.condition_name)
    ).scalars().all()
    interventions = db.execute(
        select(StagingIntervention).where(StagingIntervention.nct_id == nct_id).order_by(StagingIntervention.id)
    ).scalars().all()
    locations = db.execute(
        select(StagingLocation).where(StagingLocation.nct_id == nct_id).order_by(StagingLocation.id)
    ).scalars().all()

    return TrialDetailResponse(
        nct_id=nct_id,
        brief_title=study.brief_title,
        official_title=study.official_title,
        study_type=study.study_type,
        phase=study.phase,
        overall_status=study.overall_status,
        start_date=study.start_date,
        completion_date=study.completion_date,
        enrollment_count=study.enrollment_count,
        healthy_volunteers=study.healthy_volunteers,
        sex=study.sex,
        minimum_age=study.minimum_age,
        maximum_age=study.maximum_age,
        sponsor_name=study.sponsor_name,
        last_update_posted=study.last_update_posted,
        conditions=conditions,
        interventions=[
            {
                "intervention_type": intervention.intervention_type,
                "intervention_name": intervention.intervention_name,
            }
            for intervention in interventions
        ],
        locations=[
            {
                "facility": location.facility,
                "city": location.city,
                "state": location.state,
                "country": location.country,
            }
            for location in locations
        ],
        summary={
            "status": summary.status if summary else study.overall_status,
            "location_count": summary.location_count if summary and summary.location_count is not None else len(locations),
            "condition_count": summary.condition_count if summary and summary.condition_count is not None else len(conditions),
            "sponsor_type": summary.sponsor_type if summary else None,
        },
    )


@router.get("/{nct_id}/quality", response_model=TrialQualityResponse)
def get_trial_quality(nct_id: str, db: Session = Depends(get_db_session)) -> TrialQualityResponse:
    study_exists = db.execute(
        select(StagingStudy.nct_id).where(StagingStudy.nct_id == nct_id)
    ).scalar_one_or_none()
    if study_exists is None:
        raise HTTPException(status_code=404, detail=f"Trial {nct_id} not found")

    issues = db.execute(
        select(QualityIssue).where(QualityIssue.nct_id == nct_id).order_by(QualityIssue.detected_at.desc(), QualityIssue.id.desc())
    ).scalars().all()

    return TrialQualityResponse(
        nct_id=nct_id,
        issue_count=len(issues),
        issues=[
            {
                "issue_type": issue.issue_type,
                "issue_description": issue.issue_description,
                "detected_at": issue.detected_at,
            }
            for issue in issues
        ],
    )
