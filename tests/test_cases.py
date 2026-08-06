from core.state_manager import StateManager


# initial state of the ai agent
initial_state = {
    "mood": 5,
    "focus": 5,
    "stress": 5,
    "trust": 5,
    "motivation": 5,
    "social_engagement": 5,
    "confidence": 5
}


# create state Manager
manager = StateManager(initial_state)

# TEST CASE 1 : User wins a hackathon
print("\nTEST CASE 1 : User Wins a Hackathon")

event_1 = {
    "mood": {
        "value": 9,
        "confidence": 0.9
    },
    "motivation": {
        "value": 9,
        "confidence": 0.8
    },
    "stress": {
        "value": 2,
        "confidence": 0.7
    }
}

manager.process_event(event_1)
print(manager.get_current_state())


# TEST CASE 2 : User failed an interview
print("\nTEST CASE 2 : User Failed an Interview")

event_2 = {
    "mood": {
        "value": 2,
        "confidence": 0.9
    },
    "stress": {
        "value": 9,
        "confidence": 0.8
    },
    "motivation": {
        "value": 4,
        "confidence": 0.7
    }
}

manager.process_event(event_2)
print(manager.get_current_state())

# TEST CASE 3 : User made new friends
print("\nTEST CASE 3 : User Made New Friends")

event_3 = {
    "social_engagement": {
        "value": 9,
        "confidence": 0.9
    },
    "trust": {
        "value": 8,
        "confidence": 0.8
    },
    "mood": {
        "value": 8,
        "confidence": 0.7
    }
}

manager.process_event(event_3)
print(manager.get_current_state())


# TEST CASE 4 : Very Low Confidence Event
print("\nTEST CASE 4 : Low Confidence Event")

event_4 = {
    "mood": {
        "value": 10,
        "confidence": 0.1
    }
}

manager.process_event(event_4)
print(manager.get_current_state())

# TEST CASE 5 : Invalid Input Value Testing
print("\nTEST CASE 5 : Invalid Input Value Testing")
event_5 = {
    "mood": {
        "value": 20,
        "confidence": 1.0
    },
    "stress": {
        "value": -5,
        "confidence": 1.0
    }
}

try:
    manager.process_event(event_5)
    print(manager.get_current_state())

except ValueError as e:
    print(f"Error: {e}")