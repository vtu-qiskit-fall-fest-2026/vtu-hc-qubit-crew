
FEATURE_LABELS = {
    "upfront_fee": "Requests an upfront payment",
    "unverified_sender": "Sender identity is unverified",
    "unrealistic_pay": "Payment or rewards seem unusually high",
    "pressure_tactics": "Uses pressure or urgency tactics",
    "missing_details": "Important opportunity details are missing",
}


def explain_risk(opportunity):
    """
    Explain potential warning signs using transparent rules.

    opportunity should be a dictionary containing 0 or 1
    for each risk indicator.
    """
    warnings = []

    for feature, description in FEATURE_LABELS.items():
        value = opportunity.get(feature, 0)

        if value not in (0, 1):
            raise ValueError(
                f"{feature} must be 0 or 1."
            )

        if value == 1:
            warnings.append(description)

    risk_count = len(warnings)

    if risk_count == 0:
        level = "Fewer warning signs"
    elif risk_count <= 2:
        level = "Some warning signs"
    else:
        level = "Multiple warning signs"

    return {
        "risk_level": level,
        "warning_count": risk_count,
        "warnings": warnings,
        "message": (
            "These indicators are preliminary warning signs, "
            "not proof that an opportunity is fraudulent."
        ),
    }


if __name__ == "__main__":
    example = {
        "upfront_fee": 1,
        "unverified_sender": 1,
        "unrealistic_pay": 0,
        "pressure_tactics": 1,
        "missing_details": 1,
    }

    result = explain_risk(example)

    print("QuantumShield — Explainable Risk Check")
    print(f"Assessment: {result['risk_level']}")
    print(f"Warning signs: {result['warning_count']}")

    for warning in result["warnings"]:
        print(f"- {warning}")

    print(result["message"])
