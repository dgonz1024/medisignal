from datetime import date
from typing import Any


def validate_study_record(record: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    study = record["study"]

    if not study.get("nct_id"):
        issues.append(
            {
                "issue_type": "missing_required_field",
                "issue_description": "nct_id is missing",
            }
        )

    if not study.get("brief_title"):
        issues.append(
            {
                "issue_type": "missing_required_field",
                "issue_description": "brief_title is missing",
            }
        )

    start_date = study.get("start_date")
    completion_date = study.get("completion_date")
    if isinstance(start_date, date) and isinstance(completion_date, date) and completion_date < start_date:
        issues.append(
            {
                "issue_type": "invalid_date_ordering",
                "issue_description": "completion_date is earlier than start_date",
            }
        )

    enrollment_count = study.get("enrollment_count")
    if enrollment_count is not None and enrollment_count < 0:
        issues.append(
            {
                "issue_type": "invalid_numeric_value",
                "issue_description": "enrollment_count cannot be negative",
            }
        )

    return issues
