from app.scoring.feature_builder import build_scoring_features


def score_completion_risk(payload: dict) -> dict:
    features = build_scoring_features(payload)
    score = 0.35
    explanation: dict[str, str] = {}

    if features["location_count"] >= 10:
        score += 0.15
        explanation["location_count"] = "Higher site count increases operational complexity."
    else:
        explanation["location_count"] = "Lower site count usually reduces coordination overhead."

    if features["enrollment_count"] >= 250:
        score += 0.10
        explanation["enrollment_count"] = "Larger enrollment targets can increase completion risk."
    else:
        explanation["enrollment_count"] = "Smaller enrollment targets are often easier to complete."

    if features["phase"].lower() == "phase 1":
        score += 0.10
        explanation["phase"] = "Earlier phase studies tend to be less operationally mature."
    else:
        explanation["phase"] = "Later phase studies are often operationally better defined."

    if features["sponsor_type"].lower() == "industry":
        score -= 0.05
        explanation["sponsor_type"] = "Industry-sponsored trials may have stronger operational support."
    else:
        explanation["sponsor_type"] = "Non-industry sponsorship can vary more in operational support."

    score = max(0.0, min(score, 1.0))

    if score < 0.34:
        label = "low_risk"
    elif score < 0.67:
        label = "moderate_risk"
    else:
        label = "high_risk"

    return {
        "score": round(score, 2),
        "label": label,
        "explanation": explanation,
    }

