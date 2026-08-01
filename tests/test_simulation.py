from core.state_manager import StateManager


def test_fast_variable_changes_significantly():

    manager = StateManager({
        "mood": 5, "focus": 5, "stress": 5, "confidence": 5,
        "trust": 5, "motivation": 5, "social_engagement": 5
    })

    manager.process_event({
        "mood": {"value": 9, "confidence": 0.9}
    })

    new_state = manager.get_current_state()

    # mood is fast, should move noticeably toward 9
    assert new_state["mood"] > 6.5


def test_slow_variable_stays_stable():

    manager = StateManager({
        "mood": 5, "focus": 5, "stress": 5, "confidence": 5,
        "trust": 5, "motivation": 5, "social_engagement": 5
    })

    manager.process_event({
        "trust": {"value": 1, "confidence": 0.9}
    })

    new_state = manager.get_current_state()

    # trust is slow, should barely move even with a strong signal
    assert abs(new_state["trust"] - 5) < 1


def test_values_stay_within_range():

    manager = StateManager({
        "mood": 9, "focus": 9, "stress": 9, "confidence": 9,
        "trust": 9, "motivation": 9, "social_engagement": 9
    })

    manager.process_event({
        "mood": {"value": 10, "confidence": 1.0}
    })

    new_state = manager.get_current_state()

    for variable, value in new_state.items():
        assert 0 <= value <= 10


def test_multiple_events_sequence():

    manager = StateManager({
        "mood": 5, "focus": 5, "stress": 5, "confidence": 5,
        "trust": 5, "motivation": 5, "social_engagement": 5
    })

    manager.process_event({"mood": {"value": 9, "confidence": 0.9}})
    manager.process_event({"mood": {"value": 2, "confidence": 0.8}})

    new_state = manager.get_current_state()

    # after a big drop following a big rise, mood should be lower than the peak
    assert new_state["mood"] < 9


test_fast_variable_changes_significantly()
test_slow_variable_stays_stable()
test_values_stay_within_range()
test_multiple_events_sequence()

print("All simulation tests passed")