from core.validation import validate_signal, validate_event_signals


def test_high_confidence_signal():

    is_valid, cleaned, errors = validate_signal(
        "stress",
        {"value": 8, "confidence": 0.9}
    )

    assert is_valid is True
    assert cleaned == {"value": 8, "confidence": 0.9}


def test_low_confidence_signal():

    is_valid, cleaned, errors = validate_signal(
        "stress",
        {"value": 3, "confidence": 0.1}
    )

    assert is_valid is True
    assert cleaned["confidence"] == 0.1


def test_unknown_variable():

    is_valid, cleaned, errors = validate_signal(
        "anger",
        {"value": 5, "confidence": 0.8}
    )

    assert is_valid is False
    assert "Unknown variable" in errors[0]


def test_value_out_of_range():

    is_valid, cleaned, errors = validate_signal(
        "mood",
        {"value": 15, "confidence": 0.8}
    )

    assert is_valid is False


def test_missing_confidence_uses_default():

    is_valid, cleaned, errors = validate_signal(
        "trust",
        {"value": 6}
    )

    assert is_valid is True
    assert cleaned["confidence"] == 0.3


def test_invalid_confidence_score():

    is_valid, cleaned, errors = validate_signal(
        "focus",
        {"value": 5, "confidence": 2}
    )

    assert is_valid is False


def test_full_event_with_one_bad_signal():

    signals = {
        "stress": {"value": 8, "confidence": 0.9},
        "anger": {"value": 5, "confidence": 0.8},
    }

    clean, errors = validate_event_signals(signals)

    assert "stress" in clean
    assert "anger" not in clean
    assert len(errors) == 1


test_high_confidence_signal()
test_low_confidence_signal()
test_unknown_variable()
test_value_out_of_range()
test_missing_confidence_uses_default()
test_invalid_confidence_score()
test_full_event_with_one_bad_signal()

print("All validation tests passed")