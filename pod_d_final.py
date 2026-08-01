import math

STARTING_STATE = {
    "mood": {"value": 5, "spread": 2.0},
    "focus": {"value": 5, "spread": 2.0},
    "stress": {"value": 5, "spread": 2.0},
    "confidence": {"value": 5, "spread": 2.5},
    "motivation": {"value": 5, "spread": 2.5},
    "trust": {"value": 5, "spread": 3.5},
    "social_engagement": {"value": 5, "spread": 3.0},
}


def update_state(current_value, current_spread, suggested_value, confidence):
    variable_speed = 0.8
    effective_speed = variable_speed * confidence
    new_value = current_value + effective_speed * (suggested_value - current_value)

    shrink_factor = 1 - (confidence * 0.5)
    new_spread = current_spread * shrink_factor

    return new_value, new_spread


def get_event_timestamp(event):
    return event["timestamp"]


def get_belief_then(starting_state, events, target_date):
    current_state = {}
    for variable_name in starting_state:
        original_value = starting_state[variable_name]["value"]
        original_spread = starting_state[variable_name]["spread"]
        current_state[variable_name] = {
            "value": original_value,
            "spread": original_spread,
        }

    relevant_events = []
    for event in events:
        if event["timestamp"] <= target_date:
            relevant_events.append(event)

    relevant_events.sort(key=get_event_timestamp)

    for event in relevant_events:
        variable_name = event["variable"]

        if variable_name not in current_state:
            raise ValueError(
                "Event references unknown variable: " + str(variable_name)
            )

        old_value = current_state[variable_name]["value"]
        old_spread = current_state[variable_name]["spread"]
        suggested_value = event["suggested_value"]
        confidence = event["confidence"]

        new_value, new_spread = update_state(
            old_value, old_spread, suggested_value, confidence
        )

        current_state[variable_name]["value"] = new_value
        current_state[variable_name]["spread"] = new_spread

    return current_state


def pull_toward_later_evidence(old_value, old_spread, new_value, new_spread):
    old_var = max(old_spread ** 2, 0.0001)
    new_var = max(new_spread ** 2, 0.0001)

    old_weight = 1.0 / old_var
    new_weight = 1.0 / new_var
    total_weight = old_weight + new_weight

    pulled_value = (old_value * old_weight + new_value * new_weight) / total_weight
    pulled_spread = math.sqrt(1.0 / total_weight)

    return pulled_value, pulled_spread


def get_belief_now(starting_state, events, target_date):
    then_state = get_belief_then(starting_state, events, target_date)

    later_events = []
    for event in events:
        if event["timestamp"] > target_date:
            later_events.append(event)
    later_events.sort(key=get_event_timestamp)

    implied_state = {}
    for var, data in then_state.items():
        implied_state[var] = {"value": data["value"], "spread": data["spread"]}

    for event in later_events:
        variable_name = event["variable"]
        if variable_name not in implied_state:
            continue

        old_val = implied_state[variable_name]["value"]
        old_spr = implied_state[variable_name]["spread"]
        suggested_value = event["suggested_value"]
        signal_confidence = event["confidence"]

        new_val, new_spr = update_state(old_val, old_spr, suggested_value, signal_confidence)
        implied_state[variable_name]["value"] = new_val
        implied_state[variable_name]["spread"] = new_spr

    smoothed_state = {}
    for var in then_state:
        old_val = then_state[var]["value"]
        old_spr = then_state[var]["spread"]
        new_val = implied_state[var]["value"]
        new_spr = implied_state[var]["spread"]

        pulled_val, pulled_spr = pull_toward_later_evidence(old_val, old_spr, new_val, new_spr)
        smoothed_state[var] = {"value": pulled_val, "spread": pulled_spr}

    return smoothed_state
