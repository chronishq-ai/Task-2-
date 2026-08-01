# Core State Engine

## Overview
The Core State Engine maintains and updates the internal state of an AI agent based on incoming events and confidence scores. Each state variable is updated using a confidence-weighted state transition mechanism. The project follows a modular architecture with a shared state schema and a common update interface.

---

## State Update Formula
The state variables are updated using the following formula:

```text
new_state = current_state + effective_speed × (evidence_value - current_state)
```

where,

```text
effective_speed = variable_speed × confidence_score
```

- `current_state` : Current value of the state variable.
- `evidence_value` : New value suggested by an incoming event.
- `variable_speed` : Defines how quickly a variable can change.
- `confidence_score` : Represents the reliability of the incoming information.
- `new_state` : Updated state value.

---

## State Variables
All state variables are defined in `state_schema.json`.

Example:

```json
{
    "mood": {
        "speed": 0.7,
        "range": [0, 10]
    }
}
```

Each variable contains:
- Speed of change
- Valid value range

---

## Project Structure
```text
Chronis-intern-task/

config/
    state_schema.json

core/
    confidence_handler.py
    config_loader.py
    update_state.py
    state_manager.py

tests/
    test_cases.py

examples/
    main.py

docs/
    README.md
```

---

## File Descriptions

### state_schema.json
Stores the configuration for all state variables.
Responsibilities:
- Define variable names.
- Define variable speeds.
- Define valid state ranges.

---

### config_loader.py
Loads the shared state schema from the JSON configuration file.
Responsibilities:
- Read the state schema.
- Provide configuration data to other modules.

---

### confidence_handler.py
Implements the confidence-weighted state update logic.
Responsibilities:
- Calculate effective speed.
- Perform confidence-weighted state transitions.
- Validate input values.
- Ensure updated values remain within the allowed range.

---

### update_state.py
Acts as the public interface for updating state variables.
Responsibilities:

- Process incoming events.
- Load variable configurations.
- Call the confidence-weighted update function.
- Return the updated state.

---

### state_manager.py

Manages the current state of the AI agent.
Responsibilities:
- Store the current state.
- Process incoming events.
- Maintain state persistence.
- Return the latest state.

---

### main.py
Provides a simple example demonstrating the state update workflow.

---

### test_cases.py
Contains test scenarios for validating state updates under different conditions.

---

## State Update Workflow
```text
Incoming Event
        |
        v
   StateManager
        |
        v
    update_state()
        |
        v
  load_state_schema()
        |
        v
confidence_weighted_update()
        |
        v
   Updated State
```

---

## Confidence Handling
Confidence scores determine how strongly an incoming event influences a state variable.

Example:

```text
variable_speed = 0.7
confidence_score = 0.8

effective_speed = 0.56
```

Higher confidence values result in larger state updates, while lower confidence values produce more gradual changes.

---

## Range Validation
Each state variable is constrained by the range specified in the schema.

Example:

```text
Range = [0, 10]
```

Values are automatically clamped to remain within the allowed range.

---

## Design Principles
The Core State Engine follows:
- Modular architecture
- Shared state schema
- Confidence-weighted state transitions
- Separation of responsibilities
- State persistence
- Range validation
- Maintainable and scalable design

---

## Changes in the Current Architecture
The project was aligned with a shared architecture to maintain consistency across the team.

Key changes include:
- Replacing the Python-based variable configuration with a shared `state_schema.json`.
- Using lowercase variable names across the project.
- Reusing a common confidence-weighted update mechanism.
- Introducing a shared configuration loader.
- Organizing the project into dedicated folders for configuration, core logic, examples, tests, and documentation.

---

## Conclusion
The Core State Engine provides a simple and maintainable approach for managing AI state transitions. By combining a shared schema, confidence-weighted updates, and modular components, the system supports consistent and scalable state management.