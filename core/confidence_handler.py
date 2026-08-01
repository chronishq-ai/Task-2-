def calculate_effective_speed(
        variable_speed: float,
        confidence_score: float
) -> float:

    # Validate variable speed
    if not 0 <= variable_speed <= 1:
        raise ValueError(
            "Variable speed must be between 0 and 1"
        )

    # Validate confidence score
    if not 0 <= confidence_score <= 1:
        raise ValueError(
            "Confidence score must be between 0 and 1"
        )

    return variable_speed * confidence_score

def confidence_weighted_update(
        current_value: float,
        evidence_value: float,
        variable_speed: float,
        confidence_score: float,
        min_value: float = 0,
        max_value: float = 10
) -> float:

    # Validate allowed range
    if min_value > max_value:
        raise ValueError(
            "Minimum value cannot be greater than maximum value"
        )

    # Validate current state value
    if not min_value <= current_value <= max_value:
        raise ValueError(
            f"Current value must be between "
            f"{min_value} and {max_value}"
        )

    # Validate incoming evidence value
    if not min_value <= evidence_value <= max_value:
        raise ValueError(
            f"Evidence value must be between "
            f"{min_value} and {max_value}"
        )

    # Calculate confidence-adjusted update speed
    effective_speed = calculate_effective_speed(
        variable_speed,
        confidence_score
    )

    # Calculate new state value
    new_value = (
        current_value
        + effective_speed
        * (evidence_value - current_value)
    )

    # Keep the result within the configured state range
    new_value = max(
        min_value,
        min(new_value, max_value)
    )

    return round(new_value, 2)