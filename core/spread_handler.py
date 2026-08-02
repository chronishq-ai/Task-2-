from core.config_loader import load_state_schema


def update_spread(
    current_value,
    incoming_value,
    current_spread,
    confidence
):
    state_schema = load_state_schema()
    spread_config = state_schema["spread_config"]
    agreement_threshold = spread_config["agreement_threshold"]
    update_rate = spread_config["update_rate"]
    min_spread, max_spread = spread_config["range"]

    difference = abs(incoming_value - current_value)
    normalized_difference = difference / 10.0

    if difference <= agreement_threshold:
        agreement_strength = 1.0 - normalized_difference
        spread_change = (
            update_rate
            * confidence
            * agreement_strength
        )
        new_spread = current_spread - spread_change
    else:
        disagreement_strength = normalized_difference
        spread_change = (
            update_rate
            * confidence
            * disagreement_strength
        )
        new_spread = current_spread + spread_change

    new_spread = max(
        min_spread,
        min(new_spread, max_spread)
    )
    return new_spread
