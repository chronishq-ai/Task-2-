import json
from itertools import combinations
from dataclasses import asdict

from resolution_module import Event, compare_events


def load_events(path):
    data = json.load(open(path))
    events = []
    truth = {}
    for e in data["events"]:
        truth[e["event_id"]] = e["true_person"]
        events.append(Event(
            event_id=e["event_id"],
            calendar_name=e.get("calendar_name"),
            location=e.get("location"),
            mentioned_name=e.get("mentioned_name"),
            mentioned_relationship=e.get("mentioned_relationship"),
            time_slot=e.get("time_slot"),
        ))
    return events, truth


def run_all_pairs(events, truth):
    results = []
    ground_truth = []

    for a, b in combinations(events, 2):
        result = compare_events(a, b)
        results.append(asdict(result))
        ground_truth.append({
            "event_id_a": a.event_id,
            "event_id_b": b.event_id,
            "same_person": truth[a.event_id] == truth[b.event_id],
        })

    return results, ground_truth


if __name__ == "__main__":
    events, truth = load_events("data/test_population/events.json")
    results, ground_truth = run_all_pairs(events, truth)

    json.dump(results, open("data/ground_truth/resolution_results.json", "w"), indent=2)
    json.dump(ground_truth, open("data/ground_truth/ground_truth.json", "w"), indent=2)

    print(f"ran {len(results)} pairs across {len(events)} events")
