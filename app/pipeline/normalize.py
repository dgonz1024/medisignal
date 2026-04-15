from datetime import date, datetime
from typing import Any


def _get_nested(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first_non_empty(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None

    cleaned = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def _parse_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").strip()
        if cleaned.isdigit():
            return int(cleaned)
    return None


def _parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"yes", "true"}:
            return True
        if lowered in {"no", "false"}:
            return False
    return None


def _extract_study_type(payload: dict[str, Any]) -> str | None:
    return _first_non_empty(
        _get_nested(payload, "protocolSection", "designModule", "studyType"),
        _get_nested(payload, "Study", "ProtocolSection", "DesignModule", "StudyType"),
    )


def _extract_phase(payload: dict[str, Any]) -> str | None:
    phases = _first_non_empty(
        _get_nested(payload, "protocolSection", "designModule", "phases"),
        _get_nested(payload, "Study", "ProtocolSection", "DesignModule", "PhaseList", "Phase"),
    )
    if isinstance(phases, list):
        return ", ".join(str(phase) for phase in phases if phase)
    if isinstance(phases, str):
        return phases
    return None


def _extract_enrollment(payload: dict[str, Any]) -> int | None:
    enrollment_info = _first_non_empty(
        _get_nested(payload, "protocolSection", "designModule", "enrollmentInfo"),
        _get_nested(payload, "Study", "ProtocolSection", "DesignModule", "EnrollmentInfo"),
    )
    if isinstance(enrollment_info, dict):
        return _parse_int(_first_non_empty(enrollment_info.get("count"), enrollment_info.get("EnrollmentCount")))
    return _parse_int(enrollment_info)


def _extract_list(payload: dict[str, Any], *candidate_paths: tuple[str, ...]) -> list[Any]:
    for path in candidate_paths:
        value = _get_nested(payload, *path)
        if isinstance(value, list):
            return value
    return []


def normalize_study_record(record: dict[str, Any]) -> dict[str, Any]:
    payload = record["payload_jsonb"]

    nct_id = _first_non_empty(
        record.get("nct_id"),
        _get_nested(payload, "protocolSection", "identificationModule", "nctId"),
        _get_nested(payload, "Study", "ProtocolSection", "IdentificationModule", "NCTId"),
    )
    brief_title = _first_non_empty(
        _get_nested(payload, "protocolSection", "identificationModule", "briefTitle"),
        _get_nested(payload, "Study", "ProtocolSection", "IdentificationModule", "BriefTitle"),
    )
    official_title = _first_non_empty(
        _get_nested(payload, "protocolSection", "identificationModule", "officialTitle"),
        _get_nested(payload, "Study", "ProtocolSection", "IdentificationModule", "OfficialTitle"),
    )
    overall_status = _first_non_empty(
        _get_nested(payload, "protocolSection", "statusModule", "overallStatus"),
        _get_nested(payload, "Study", "ProtocolSection", "StatusModule", "OverallStatus"),
    )
    start_date_value = _first_non_empty(
        _get_nested(payload, "protocolSection", "statusModule", "startDateStruct", "date"),
        _get_nested(payload, "Study", "ProtocolSection", "StatusModule", "StartDateStruct", "StartDate"),
    )
    completion_date_value = _first_non_empty(
        _get_nested(payload, "protocolSection", "statusModule", "completionDateStruct", "date"),
        _get_nested(payload, "Study", "ProtocolSection", "StatusModule", "CompletionDateStruct", "CompletionDate"),
    )
    last_update_value = _first_non_empty(
        _get_nested(payload, "protocolSection", "statusModule", "lastUpdatePostDateStruct", "date"),
        _get_nested(payload, "Study", "ProtocolSection", "StatusModule", "LastUpdatePostDateStruct", "LastUpdatePostDate"),
    )
    eligibility_module = _first_non_empty(
        _get_nested(payload, "protocolSection", "eligibilityModule"),
        _get_nested(payload, "Study", "ProtocolSection", "EligibilityModule"),
        {},
    )
    sponsor_name = _first_non_empty(
        _get_nested(payload, "protocolSection", "sponsorCollaboratorsModule", "leadSponsor", "name"),
        _get_nested(payload, "Study", "ProtocolSection", "SponsorCollaboratorsModule", "LeadSponsor", "LeadSponsorName"),
    )

    condition_values = _extract_list(
        payload,
        ("derivedSection", "conditionBrowseModule", "meshes"),
        ("protocolSection", "conditionsModule", "conditions"),
        ("Study", "ProtocolSection", "ConditionsModule", "ConditionList", "Condition"),
    )
    if condition_values and isinstance(condition_values[0], dict):
        conditions = [
            {"nct_id": nct_id, "condition_name": item.get("term")}
            for item in condition_values
            if item.get("term")
        ]
    else:
        conditions = [
            {"nct_id": nct_id, "condition_name": condition}
            for condition in condition_values
            if isinstance(condition, str) and condition.strip()
        ]

    intervention_values = _extract_list(
        payload,
        ("protocolSection", "armsInterventionsModule", "interventions"),
        ("Study", "ProtocolSection", "ArmsInterventionsModule", "InterventionList", "Intervention"),
    )
    interventions: list[dict[str, Any]] = []
    for intervention in intervention_values:
        if not isinstance(intervention, dict):
            continue
        intervention_type = _first_non_empty(intervention.get("type"), intervention.get("InterventionType"))
        intervention_name = _first_non_empty(intervention.get("name"), intervention.get("InterventionName"))
        if intervention_name:
            interventions.append(
                {
                    "nct_id": nct_id,
                    "intervention_type": intervention_type,
                    "intervention_name": intervention_name,
                }
            )

    location_values = _extract_list(
        payload,
        ("protocolSection", "contactsLocationsModule", "locations"),
        ("Study", "ProtocolSection", "ContactsLocationsModule", "LocationList", "Location"),
    )
    locations: list[dict[str, Any]] = []
    for location in location_values:
        if not isinstance(location, dict):
            continue
        facility = _first_non_empty(
            _get_nested(location, "facility"),
            _get_nested(location, "LocationFacility"),
            _get_nested(location, "LocationFacility", "Name"),
        )
        location_contacts = _first_non_empty(location.get("LocationContactList"), {})
        city = _first_non_empty(
            location.get("city"),
            location.get("LocationCity"),
            location.get("LocationAddressCity"),
        )
        state = _first_non_empty(
            location.get("state"),
            location.get("LocationState"),
            location.get("LocationAddressState"),
        )
        country = _first_non_empty(
            location.get("country"),
            location.get("LocationCountry"),
            location.get("LocationAddressCountry"),
        )
        if facility or city or state or country:
            locations.append(
                {
                    "nct_id": nct_id,
                    "facility": facility,
                    "city": city,
                    "state": state,
                    "country": country,
                }
            )

    return {
        "study": {
            "nct_id": nct_id,
            "brief_title": brief_title,
            "official_title": official_title,
            "study_type": _extract_study_type(payload),
            "phase": _extract_phase(payload),
            "overall_status": overall_status,
            "start_date": _parse_date(start_date_value),
            "completion_date": _parse_date(completion_date_value),
            "enrollment_count": _extract_enrollment(payload),
            "healthy_volunteers": _parse_bool(
                _first_non_empty(eligibility_module.get("healthyVolunteers"), eligibility_module.get("HealthyVolunteers"))
            ),
            "sex": _first_non_empty(eligibility_module.get("sex"), eligibility_module.get("Gender")),
            "minimum_age": _first_non_empty(eligibility_module.get("minimumAge"), eligibility_module.get("MinimumAge")),
            "maximum_age": _first_non_empty(eligibility_module.get("maximumAge"), eligibility_module.get("MaximumAge")),
            "sponsor_name": sponsor_name,
            "last_update_posted": _parse_date(last_update_value),
        },
        "conditions": conditions,
        "interventions": interventions,
        "locations": locations,
    }
