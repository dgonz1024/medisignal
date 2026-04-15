def build_scoring_features(payload: dict) -> dict:
    return {
        "phase": payload["phase"],
        "enrollment_count": payload["enrollment_count"],
        "location_count": payload["location_count"],
        "condition_count": payload["condition_count"],
        "sponsor_type": payload["sponsor_type"],
    }

