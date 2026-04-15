from datetime import date, datetime

from pydantic import BaseModel, Field


class TrialListItem(BaseModel):
    nct_id: str
    brief_title: str | None
    phase: str | None
    status: str | None
    enrollment_count: int | None
    location_count: int | None
    condition_count: int | None
    sponsor_name: str | None
    sponsor_type: str | None


class TrialListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    results: list[TrialListItem]


class TrialIntervention(BaseModel):
    intervention_type: str | None
    intervention_name: str


class TrialLocation(BaseModel):
    facility: str | None
    city: str | None
    state: str | None
    country: str | None


class TrialDetailSummary(BaseModel):
    status: str | None
    location_count: int
    condition_count: int
    sponsor_type: str | None


class TrialDetailResponse(BaseModel):
    nct_id: str
    brief_title: str | None
    official_title: str | None
    study_type: str | None
    phase: str | None
    overall_status: str | None
    start_date: date | None
    completion_date: date | None
    enrollment_count: int | None
    healthy_volunteers: bool | None
    sex: str | None
    minimum_age: str | None
    maximum_age: str | None
    sponsor_name: str | None
    last_update_posted: date | None
    conditions: list[str]
    interventions: list[TrialIntervention]
    locations: list[TrialLocation]
    summary: TrialDetailSummary


class QualityIssueItem(BaseModel):
    issue_type: str
    issue_description: str
    detected_at: datetime


class TrialQualityResponse(BaseModel):
    nct_id: str
    issue_count: int
    issues: list[QualityIssueItem]


class ConditionStatsItem(BaseModel):
    condition_name: str
    trial_count: int
    avg_enrollment: float | None


class ConditionStatsResponse(BaseModel):
    count: int
    results: list[ConditionStatsItem]


class SponsorStatsItem(BaseModel):
    sponsor_name: str
    trial_count: int
    completion_rate: float | None = Field(
        default=None,
        description="Approximate fraction of studies in a completed-style status.",
    )


class SponsorStatsResponse(BaseModel):
    count: int
    results: list[SponsorStatsItem]


class StatusBucketItem(BaseModel):
    status_bucket: str
    trial_count: int
    share_of_trials: float


class StatusOverviewResponse(BaseModel):
    total_trials: int
    terminated_early_trials: int
    terminated_early_rate: float
    buckets: list[StatusBucketItem]


class TerminationStatsItem(BaseModel):
    group_name: str
    trial_count: int
    terminated_early_count: int
    terminated_early_rate: float


class TerminationStatsResponse(BaseModel):
    count: int
    results: list[TerminationStatsItem]


class ConditionCoverageItem(BaseModel):
    condition_name: str
    trial_count: int
    coverage_label: str


class ConditionCoverageResponse(BaseModel):
    count: int
    low_coverage_threshold: int
    results: list[ConditionCoverageItem]


class StatusCountItem(BaseModel):
    label: str
    trial_count: int


class SponsorDetailResponse(BaseModel):
    sponsor_name: str
    trial_count: int
    completion_rate: float
    terminated_early_count: int
    terminated_early_rate: float
    average_enrollment: float | None
    phase_distribution: list[StatusCountItem]
    status_distribution: list[StatusCountItem]
    top_conditions: list[StatusCountItem]


class ConditionDetailResponse(BaseModel):
    condition_name: str
    trial_count: int
    recruiting_count: int
    completed_count: int
    terminated_early_count: int
    terminated_early_rate: float
    average_enrollment: float | None
    sponsor_type_distribution: list[StatusCountItem]
    phase_distribution: list[StatusCountItem]
    status_distribution: list[StatusCountItem]


class AutocompleteResponse(BaseModel):
    field: str
    query: str
    count: int
    suggestions: list[str]
