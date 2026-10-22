
from src.explanations import explain_risk


def assess_opportunity(opportunity):
    """
    Return a structured, explainable assessment of an opportunity.

    Expected input: a dictionary with five risk indicators,
    each set to 0 (not observed) or 1 (observed).
    """
    required_features = [
        "upfront_fee",
        "unverified_sender",
        "unrealistic_pay",
        "pressure_tactics",
        "missing_details",
    ]

    missing = [
        feature
        for feature in required_features
        if feature not in opportunity
    ]

    if missing:
        raise ValueError(
            f"Missing required indicators: {', '.join(missing)}"
        )

    explanation = explain_risk(opportunity)

    return {
        "assessment": explanation["risk_level"],
        "warning_count": explanation["warning_count"],
        "warnings": explanation["warnings"],
        "disclaimer": explanation["message"],
    }


if __name__ == "__main__":
    example_opportunity = {
        "upfront_fee": 1,
        "unverified_sender": 1,
        "unrealistic_pay": 0,
        "pressure_tactics": 1,
        "missing_details": 1,
    }

    result = assess_opportunity(example_opportunity)

    print("QuantumShield — Opportunity Assessment")
    print(f"Assessment: {result['assessment']}")
    print(f"Warning signs: {result['warning_count']}")

    for warning in result["warnings"]:
        print(f"- {warning}")

    print(f"\nNote: {result['disclaimer']}")
