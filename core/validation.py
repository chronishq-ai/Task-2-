from core.config_loader import load_state_schema

DEFAULT_CONFIDENCE = 0.3
# Used when Pod B does not send a confidence score

def validate_signal(variable_name, signal):
    errors = []

    schema = load_state_schema()
    variables = schema["variables"]

    # Check whether variable exists in shared schema
    if variable_name not in variables:
        errors.append(
            f"Unknown variable: {variable_name}"
        )
        return False, None, errors

    # Check whether value exists
    if "value" not in signal:
        errors.append(
            f"Missing 'value' for {variable_name}"
        )
        return False, None, errors

    value = signal["value"]

    # Check value type
    if not isinstance(value, (int, float)):
        errors.append(
            f"{variable_name} value must be numeric"
        )
        return False, None, errors

    # Get allowed value range from schema
    min_value, max_value = variables[variable_name]["range"]

    if not min_value <= value <= max_value:
        errors.append(
            f"{variable_name} value {value} is out of range "
            f"({min_value}-{max_value})"
        )
        return False, None, errors

    # Use default confidence if confidence is missing
    confidence = signal.get(
        "confidence",
        DEFAULT_CONFIDENCE
    )

    # Check confidence type
    if not isinstance(confidence, (int, float)):
        errors.append(
            f"{variable_name} confidence must be numeric"
        )
        return False, None, errors

    # Confidence must remain between 0 and 1
    if not 0 <= confidence <= 1:
        errors.append(
            f"{variable_name} confidence {confidence} "
            f"is out of range (0-1)"
        )
        return False, None, errors

    cleaned = {
        "value": value,
        "confidence": confidence
    }

    return True, cleaned, errors


def validate_event_signals(signals):
    clean_signals = {}
    all_errors = []

    for variable_name, signal in signals.items():

        is_valid, cleaned, errors = validate_signal(
            variable_name,
            signal
        )

        if is_valid:
            clean_signals[variable_name] = cleaned
        else:
            all_errors.extend(errors)

    return clean_signals, all_errors