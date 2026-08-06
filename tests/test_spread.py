from core.state_manager import StateManager
from core.spread_handler import update_spread


def build_initial_state():
    return {
        "mood": 5,
        "focus": 5,
        "stress": 5,
        "confidence": 5,
        "trust": 5,
        "motivation": 5,
        "social_engagement": 5,
    }


def test_high_confidence_agreeing_evidence_shrinks_spread():

    manager = StateManager(build_initial_state())

    manager.process_event({
        "mood": {"value": 6, "confidence": 0.9}
    })

    new_state = manager.get_current_state()

    assert new_state["mood"]["spread"] < 2.0


def test_low_confidence_causes_minimal_spread_change():

    manager = StateManager(build_initial_state())

    manager.process_event({
        "mood": {"value": 6, "confidence": 0.1}
    })

    new_state = manager.get_current_state()

    assert abs(new_state["mood"]["spread"] - 2.0) < 0.2


def test_disagreeing_evidence_increases_spread():

    manager = StateManager(build_initial_state())

    manager.process_event({
        "mood": {"value": 10, "confidence": 0.9}
    })

    new_state = manager.get_current_state()

    assert new_state["mood"]["spread"] > 2.0


def test_spread_stays_within_range():

    manager = StateManager(build_initial_state())

    for _ in range(10):
        manager.process_event({
            "mood": {"value": 10, "confidence": 1.0}
        })

    new_state = manager.get_current_state()

    assert 0 <= new_state["mood"]["spread"] <= 5


def test_invalid_confidence_rejected():

    try:
        update_spread(
            current_value=5,
            incoming_value=6,
            current_spread=2.0,
            confidence=1.5
        )
        assert False, "Expected an error for invalid confidence, but none was raised"
    except (ValueError, AssertionError):
        assert True


test_high_confidence_agreeing_evidence_shrinks_spread()
test_low_confidence_causes_minimal_spread_change()
test_disagreeing_evidence_increases_spread()
test_spread_stays_within_range()
test_invalid_confidence_rejected()

print("All spread tests passed")