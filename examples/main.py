from core.state_manager import StateManager

# Initial state of AI agent
initial_state = {
    "mood": 5,
    "focus": 5,
    "stress": 5,
    "trust": 5,
    "motivation": 5,
    "social_engagement": 5
}

# Create State Manager
manager = StateManager(initial_state)

# Simulate an incoming event
incoming_event = {
    "mood": {
        "value": 9,
        "confidence": 0.8
    },

    "motivation": {
        "value": 8,
        "confidence": 0.9
    },

    "stress": {
        "value": 2,
        "confidence": 0.7
    }
}

# Process the event
manager.process_event(incoming_event)

# Print updated state of AI agent
print("Updated State:")
print(manager.get_current_state())