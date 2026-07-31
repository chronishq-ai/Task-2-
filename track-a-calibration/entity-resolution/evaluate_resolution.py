import json

THRESHOLD = 0.5  # probability >= this counts as "predicted same person"


def load_data():
    results = json.load(open("data/ground_truth/resolution_results.json"))
    truth = json.load(open("data/ground_truth/ground_truth.json"))
    truth_lookup = {(t["event_id_a"], t["event_id_b"]): t["same_person"] for t in truth}
    return results, truth_lookup


def evaluate(results, truth_lookup):
    tp = fp = tn = fn = 0
    conflation_errors = []   # predicted same, actually different
    splitting_errors = []    # predicted different, actually same

    for r in results:
        key = (r["event_id_a"], r["event_id_b"])
        actual_same = truth_lookup[key]
        predicted_same = r["same_person_probability"] >= THRESHOLD

        if predicted_same and actual_same:
            tp += 1
        elif predicted_same and not actual_same:
            fp += 1
            conflation_errors.append(r)
        elif not predicted_same and actual_same:
            fn += 1
            splitting_errors.append(r)
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0

    return {
        "true_positive": tp, "false_positive": fp,
        "true_negative": tn, "false_negative": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
    }, conflation_errors, splitting_errors


if __name__ == "__main__":
    results, truth_lookup = load_data()
    metrics, conflation, splitting = evaluate(results, truth_lookup)

    print(json.dumps(metrics, indent=2))
    print(f"\nconflation errors (worse - two people treated as one): {len(conflation)}")
    print(f"splitting errors (cheaper to fix - one person treated as two): {len(splitting)}")

    json.dump(metrics, open("data/ground_truth/precision_recall.json", "w"), indent=2)
    json.dump({"conflation": conflation, "splitting": splitting},
              open("data/ground_truth/errors_breakdown.json", "w"), indent=2)
