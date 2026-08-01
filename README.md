# Chronis-AI Pod D: Belief Smoothing Engine (v0.2)

## Project Overview

This repository contains **v0.2** of the Chronis-AI belief smoothing engine developed by **Pod D**. 

The core objective of this project is to implement a retroactive belief state adjustment—comparing what an AI system believed at a specific time in the past (**"Then"**) versus what it *should* have believed given subsequent evidence that emerged later (**"Now"**). This is achieved through a "backward smoothing" algorithm that pulls past estimates towards later evidence using inverse-variance weighting.

## Key Features

- **Forward Filtering ("Then" State)**: Implemented in `get_belief_then`. It acts as a forward filter up to a target date, processing only events that occurred on or before that date. This serves as the baseline belief state.
- **Backward Smoothing ("Now" State)**: Implemented in `get_belief_now`. It runs later events forward from the "Then" state to get an "implied" state, and then pulls the original "Then" estimate toward this implied state. 
- **Inverse-Variance Weighting**: The pull towards later evidence is weighted mathematically using the `spread` (uncertainty). Lower spread indicates higher confidence, resulting in a stronger influence on the blended result.
- **Automated Validation & Testing**: Built-in synthetic tests ensure the mathematical integrity of high/low confidence scaling, date boundaries, and spread reduction.
- **Presentation-Ready Output**: The system outputs a clear, tabular comparison showing the variable, its "Then" value and spread, its "Now" value and spread, the delta, and a plain-language analysis of why the shift occurred based on the event timeline.

## Repository Structure

- `POD_D_v0.2 (1) (1).py`
  The main engine script for version 0.2. It contains the core smoothing logic (`get_belief_then`, `get_belief_now`, `pull_toward_later_evidence`), the unit test suite, and the demonstration runner with the tabular analysis output.
  
- `POD_D_Kuheli_task2-2 (2) (1).py`
  An earlier development script focusing primarily on the forward-filtering `"Then"` state calculation before the inverse-variance backward smoothing was fully integrated.

- `professor_life_dataset_45_events_clean.json`
  The core testing dataset containing a chronological log of 45 "Professor Life" events. Each event provides signals across 7 key variables (mood, focus, stress, confidence, motivation, trust, social_engagement) along with confidence and spread metrics.

- `Pod_D_Human_Validation_Explanation.pdf`
  Documentation detailing the "Then vs. Now" logic and providing context for the human validators evaluating the system's output.

- `Pod_D_Human_Validation_Responses.pdf`
  The recorded responses and feedback from external validators who confirmed whether the retroactive "Now" belief adjustments better matched their intuition compared to the standard "Then" baseline.

## Getting Started

### Prerequisites
- Python 3.x
- No external pip dependencies are required (relies on standard libraries: `json`, `math`).

### Execution

To run the automated tests and see the belief state comparison on the real dataset, execute the main v0.2 script from your terminal:

```bash
python "POD_D_v0.2 (1) (1).py"
```

### Expected Output

1. **Test Suite Results**: The script will first run a suite of synthetic tests to prove the mathematical logic works as intended (e.g., verifying that high confidence shrinks the spread noticeably).
2. **Belief State Comparison**: A formatted table comparing the "Then" vs. "Now" belief states on the target date (e.g., `2026-02-05`), showing exact values, spreads (uncertainty), and directional shifts.
3. **Plain-Language Analysis**: A detailed breakdown for each tracked variable explaining *why* the belief changed (or didn't change) based on specific later events from the dataset.

## Mathematical Core

The blending function in `POD_D_v0.2 (1) (1).py` relies on **Inverse-Variance Weighting**:

```python
old_weight = 1.0 / (old_spread ** 2)
new_weight = 1.0 / (new_spread ** 2)
total_weight = old_weight + new_weight

pulled_value = (old_value * old_weight + new_value * new_weight) / total_weight
pulled_spread = math.sqrt(1.0 / total_weight)
```
This ensures that as more data is collected, the uncertainty (spread) is mathematically guaranteed to decrease, demonstrating that hindsight increases the system's confidence in past states.