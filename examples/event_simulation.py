from core.state_manager import StateManager


# Starting state — everything neutral at 5
initial_state = {
    "mood": 5,
    "focus": 5,
    "stress": 5,
    "confidence": 5,
    "trust": 5,
    "motivation": 5,
    "social_engagement": 5
}


# Realistic test events — mix of positive, negative, neutral
test_events = [
    {
        "name": "Got promoted at work",
        "signals": {
            "mood": {"value": 9, "confidence": 0.9},
            "confidence": {"value": 8, "confidence": 0.8},
            "motivation": {"value": 9, "confidence": 0.9}
        }
    },
    {
        "name": "Missed an important deadline",
        "signals": {
            "stress": {"value": 9, "confidence": 0.9},
            "focus": {"value": 3, "confidence": 0.7},
            "confidence": {"value": 3, "confidence": 0.6}
        }
    },
    {
        "name": "Had a great workout",
        "signals": {
            "mood": {"value": 8, "confidence": 0.8},
            "stress": {"value": 3, "confidence": 0.6}
        }
    },
    {
        "name": "Regular day at work, nothing notable",
        "signals": {
            "focus": {"value": 5, "confidence": 0.4}
        }
    },
    {
        "name": "Reconnected with an old friend",
        "signals": {
            "trust": {"value": 7, "confidence": 0.6},
            "social_engagement": {"value": 8, "confidence": 0.7},
            "mood": {"value": 7, "confidence": 0.7}
        }
    },
    {
        "name": "Argument with a close friend",
        "signals": {
            "trust": {"value": 3, "confidence": 0.7},
            "mood": {"value": 3, "confidence": 0.8},
            "stress": {"value": 7, "confidence": 0.7}
        }
    },
]


def run_simulation():

    manager = StateManager(initial_state.copy())

    print("Starting state:")
    print(manager.get_current_state())
    print()

    for event in test_events:
        manager.process_event(event["signals"])
        print(f"After event: {event['name']}")
        print(manager.get_current_state())
        print()


if __name__ == "__main__":
    run_simulation()