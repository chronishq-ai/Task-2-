# chronis-ai — Demo 2 Script (v0.2)
Pod E — Hridhani J

---

## Before the demo
- Confirm `.env` has a working GEMINI_API_KEY (free tier) on the demo machine.
- Run `python3 cli.py demo` once, quietly, right before presenting — just to
  confirm the environment is warm and nothing broke overnight.
- Delete `events.json` and `events.db` right before starting, so the demo
  starts from a clean slate.

---

## Opening (say this first)
"This is chronis-ai — a personal memory assistant. It tracks seven things
about a person over time: mood, focus, stress, confidence, trust,
motivation, and social engagement. Every variable carries both a value
*and* a spread — how confident the system is in that value. As new events
come in, both get updated. And critically, it can look back and revise
what it believed about the past, once later events reveal more context."

---

## Step 1 — Add the first event
**Type:**
```
python3 cli.py add-event "felt confident presenting to the team"
```
**Say:** "Here's an event that sounds positive on its own. Watch what the
system pulls out of it — a value and a confidence score, for whichever
variables it thinks are actually affected."

*(Real Pod B will return something like: confidence up, mood up, with
per-variable confidence scores — read a couple out loud from the output.)*

---

## Step 2 — Query what we believe right now
**Type:**
```
python3 cli.py query 2026-08-02
```
**Say:** "This is what the system currently believes — both a value and a
spread for every tracked variable. Notice trust barely moved, because
trust is designed to change slowly — even a strong signal only nudges it
a little."

---

## Step 3 — Add the reveal event
**Type:**
```
python3 cli.py add-event "the presentation actually went badly and caused ongoing stress"
```
**Say:** "Now here's a later event that reveals the truth behind the
first one."

---

## Step 4 — Query the SAME earlier date again
**Type:**
```
python3 cli.py query 2026-08-02
```
**Say:** "Watch — the answer for that same moment just changed. The
system pulled its past belief toward what the later evidence implies,
weighted by how confident each estimate was. That's not just 'more data
means a different average' — it's backward smoothing, and the spread
shrank too, meaning it's more confident in the revised answer."

---

## Step 5 — Show the storage layer (optional, if time allows)
**Type:**
```
python3 cli.py storage-stats
```
**Say:** "Every event is stored permanently, append-only, in a real
database — and the system automatically checkpoints every 5 events, so
looking up 'what did we believe on this date' doesn't require replaying
the entire history from scratch."

---

## Closing
"Every piece here is real, tested code — Pod A's confidence-weighted
state engine, Pod B's LLM-based event understanding, Pod C's checkpointed
storage, and Pod D's backward smoothing — wired into one command-line
tool. If Pod B's API call ever fails live, the system falls back
automatically rather than breaking the demo."

---

## Honesty note for rehearsal
This script currently uses the same scripted "presentation went badly"
scenario from v0.1 — not real pilot-week data, since pilot recruitment
didn't happen this cycle given the time available. State this plainly if
asked, rather than presenting it as pilot data. If there's time before
submission, swapping in one real typed event (even from a teammate) for
Step 1 would satisfy the "real week of typed-in events" spirit of v0.2
more fully.

---

## Fallback plan
If Pod B's live API call fails during the actual demo (network, rate
limit), the CLI automatically falls back to the placeholder — the demo
still runs, just say: "This one's using our fallback logic — worth
noting that's a built-in safety net, not a crash."
