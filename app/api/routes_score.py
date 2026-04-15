from fastapi import APIRouter
from pydantic import BaseModel

from app.scoring.baseline_score import score_completion_risk

router = APIRouter(prefix="/score", tags=["score"])


class CompletionRiskRequest(BaseModel):
    phase: str
    enrollment_count: int
    location_count: int
    condition_count: int
    sponsor_type: str


@router.post("/completion-risk")
def completion_risk(payload: CompletionRiskRequest) -> dict:
    return score_completion_risk(payload.model_dump())

