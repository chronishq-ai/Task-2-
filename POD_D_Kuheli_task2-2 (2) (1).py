import json

# STEP 1: Pod A's finalized starting state (unchanged)

STARTING_STATE = {
    "mood": {"value": 5, "spread": 2.0},
    "focus": {"value": 5, "spread": 2.0},
    "stress": {"value": 5, "spread": 2.0},
    "confidence": {"value": 5, "spread": 2.5},
    "motivation": {"value": 5, "spread": 2.5},
    "trust": {"value": 5, "spread": 3.5},
    "social_engagement": {"value": 5, "spread": 3.0},
}



# STEP 2: update_state -- value formula confirmed by Pod A, spread still placeholder

def update_state(current_value, current_spread, suggested_value, confidence):
    variable_speed = 0.8 #assumed

    effective_speed = variable_speed * confidence
    new_value = current_value + effective_speed * (suggested_value - current_value)

    shrink_factor = 1 - (confidence * 0.5)
    new_spread = current_spread * shrink_factor

    return new_value, new_spread



# STEP 3: sorting helper (unchanged, no lambda)

def get_event_timestamp(event):
    return event["timestamp"]



# STEP 4: get_belief_then, with the date-boundary bug fixed

def get_belief_then(starting_state, events, target_date):
    current_state = {}
    for variable_name in starting_state:
        original_value = starting_state[variable_name]["value"]
        original_spread = starting_state[variable_name]["spread"]
        current_state[variable_name] = {
            "value": original_value,
            "spread": original_spread,
        }

    target_date_only = target_date[:10]

    relevant_events = []
    for event in events:
        event_date_only = event["timestamp"][:10]
        if event_date_only <= target_date_only:
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

# STEP 5: adapter -- flattens Mayank's real "signals" events into the

DEFAULT_CONFIDENCE = 0.7  


def flatten_raw_event(raw_event, default_confidence):
    flattened_entries = []
    for variable_name, signal in raw_event["signals"].items():
        flattened_entries.append({
            "timestamp": raw_event["timestamp"],
            "variable": variable_name,
            "suggested_value": signal["value"],
            "confidence": default_confidence,
        })
    return flattened_entries


def load_real_events(json_path, default_confidence=DEFAULT_CONFIDENCE):
    with open(json_path, "r") as f:
        raw_events = json.load(f)

    all_events = []
    for raw_event in raw_events:
        all_events.extend(flatten_raw_event(raw_event, default_confidence))

    return all_events



# STEP 6: synthetic test events -- KEPT AS-IS for the automated tests below,
# separate from the real dataset, since these are hand-designed to test
# specific behaviors (high/low confidence, date boundaries)

SAMPLE_EVENTS = [
    {
        "timestamp": "2026-07-20",
        "variable": "confidence",
        "suggested_value": 3,
        "confidence": 0.9,
    },
    {
        "timestamp": "2026-07-21",
        "variable": "stress",
        "suggested_value": 8,
        "confidence": 0.85,
    },
    {
        "timestamp": "2026-07-23",
        "variable": "confidence",
        "suggested_value": 7,
        "confidence": 0.2,
    },
]

# STEP 7: automated tests (unchanged logic, still all pass)

def test_output_shape_is_correct():
    result = get_belief_then(STARTING_STATE, SAMPLE_EVENTS, "2026-07-24")
    for variable_name in result:
        assert "value" in result[variable_name]
        assert "spread" in result[variable_name]
    print("PASS: test_output_shape_is_correct")


def test_high_confidence_shrinks_spread_noticeably():
    starting_spread = STARTING_STATE["confidence"]["spread"]
    one_event = [{"timestamp": "2026-07-20", "variable": "confidence",
                  "suggested_value": 3, "confidence": 0.9}]
    result = get_belief_then(STARTING_STATE, one_event, "2026-07-25")
    ending_spread = result["confidence"]["spread"]
    assert ending_spread < starting_spread
    assert ending_spread < starting_spread * 0.8
    print("PASS: test_high_confidence_shrinks_spread_noticeably")
    print("  starting spread:", starting_spread, "-> ending spread:", ending_spread)


def test_low_confidence_barely_moves_spread():
    starting_spread = STARTING_STATE["confidence"]["spread"]
    one_event = [{"timestamp": "2026-07-20", "variable": "confidence",
                  "suggested_value": 9, "confidence": 0.1}]
    result = get_belief_then(STARTING_STATE, one_event, "2026-07-25")
    ending_spread = result["confidence"]["spread"]
    assert ending_spread > starting_spread * 0.9
    print("PASS: test_low_confidence_barely_moves_spread")
    print("  starting spread:", starting_spread, "-> ending spread:", ending_spread)


def test_events_after_target_date_are_ignored():
    events_plus_future = SAMPLE_EVENTS + [
        {"timestamp": "2026-07-30", "variable": "mood",
         "suggested_value": 10, "confidence": 1.0}
    ]
    result = get_belief_then(STARTING_STATE, events_plus_future, "2026-07-24")
    assert result["mood"]["value"] == STARTING_STATE["mood"]["value"]
    assert result["mood"]["spread"] == STARTING_STATE["mood"]["spread"]
    print("PASS: test_events_after_target_date_are_ignored")


def test_unknown_variable_raises_error():
    bad_event = [{"timestamp": "2026-07-20", "variable": "made_up_variable",
                  "suggested_value": 5, "confidence": 0.5}]
    raised_error = False
    try:
        get_belief_then(STARTING_STATE, bad_event, "2026-07-24")
    except ValueError:
        raised_error = True
    assert raised_error
    print("PASS: test_unknown_variable_raises_error")


def test_timestamped_event_on_target_date_is_included():
    event_on_target_date = [{
        "timestamp": "2026-01-10T09:00",
        "variable": "mood",
        "suggested_value": 10,
        "confidence": 1.0,
    }]
    result = get_belief_then(STARTING_STATE, event_on_target_date, "2026-01-10")
    assert result["mood"]["value"] > STARTING_STATE["mood"]["value"], (
        "Event on the target date was wrongly excluded (date-boundary bug)"
    )
    print("PASS: test_timestamped_event_on_target_date_is_included")

# STEP 8: run tests, then demo on the REAL dataset

if __name__ == "__main__":
    print("Running tests on synthetic events...\n")
    test_output_shape_is_correct()
    test_high_confidence_shrinks_spread_noticeably()
    test_low_confidence_barely_moves_spread()
    test_events_after_target_date_are_ignored()
    test_unknown_variable_raises_error()
    test_timestamped_event_on_target_date_is_included()
    print("\nAll tests passed.\n")

    print("Loading Mayank's real dataset...")
    real_events = load_real_events("professor_life_dataset_45_events_clean.json")
    print("Loaded", len(real_events), "flattened signal entries "
          "(45 events x 7 variables each).\n")

    target_date = "2026-02-05"
    print("Real 'then' answer for target_date =", target_date, ":")
    final_state = get_belief_then(STARTING_STATE, real_events, target_date)
    for variable_name in final_state:
        value = final_state[variable_name]["value"]
        spread = final_state[variable_name]["spread"]
        print(" ", variable_name, "-> value:", round(value, 2), "spread:", round(spread, 2))