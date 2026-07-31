import json
from dataclasses import dataclass, asdict


@dataclass
class Event:
    event_id: str
    calendar_name: str = None       # name from a calendar entry, if any
    location: str = None             # recurring location tag, if any
    mentioned_name: str = None       # a name said out loud, if any
    mentioned_relationship: str = None  # e.g. "mom", "my manager" - used when no name is said
    time_slot: str = None            # e.g. "tue_evening"


@dataclass
class ResolutionResult:
    event_id_a: str
    event_id_b: str
    same_person_probability: float
    confidence: float
    signals_used: list
    rationale: str


def compare_events(a: Event, b: Event) -> ResolutionResult:
    signal_hits = []
    signal_misses = []

    if a.calendar_name and b.calendar_name:
        if a.calendar_name == b.calendar_name:
            signal_hits.append("calendar_name")
        else:
            signal_misses.append("calendar_name")

    if a.location and b.location:
        if a.location == b.location:
            signal_hits.append("location")
        else:
            signal_misses.append("location")

    if a.mentioned_name and b.mentioned_name:
        if a.mentioned_name == b.mentioned_name:
            signal_hits.append("mentioned_name")
        else:
            signal_misses.append("mentioned_name")

    if a.mentioned_relationship and b.mentioned_relationship:
        if a.mentioned_relationship == b.mentioned_relationship:
            signal_hits.append("mentioned_relationship")
        else:
            signal_misses.append("mentioned_relationship")

    if a.time_slot and b.time_slot:
        if a.time_slot == b.time_slot:
            signal_hits.append("time_slot")
        else:
            signal_misses.append("time_slot")

    total_checked = len(signal_hits) + len(signal_misses)

    if total_checked == 0:
        # nothing overlaps between the two events at all - genuinely unknown
        return ResolutionResult(a.event_id, b.event_id, 0.5, 0.1, [], "no overlapping signal available")

    hit_ratio = len(signal_hits) / total_checked

    # a first-name-only match is weak evidence on its own (two people can share
    # a name) - so a name hit without location/calendar backup gets discounted
    name_only = signal_hits == ["mentioned_name"] and "location" not in signal_hits

    probability = hit_ratio
    if name_only:
        probability = min(probability, 0.6)

    # confidence scales with how much signal we actually had to check, and
    # drops further for the name-only ambiguous case
    confidence = min(0.3 + 0.15 * total_checked, 0.9)
    if name_only:
        confidence = min(confidence, 0.5)

    rationale = f"matched on {signal_hits}, mismatched on {signal_misses}"

    return ResolutionResult(a.event_id, b.event_id, round(probability, 3), round(confidence, 3), signal_hits, rationale)


if __name__ == "__main__":
    # one dummy pair, to confirm it runs end to end
    e1 = Event(event_id="e1", calendar_name="Priya", location="office_coffee_shop", time_slot="tue_morning")
    e2 = Event(event_id="e2", calendar_name="Priya", location="office_coffee_shop", time_slot="tue_morning")

    result = compare_events(e1, e2)
    print(json.dumps(asdict(result), indent=2))
