# Failure Modes - Entity Resolution

## Numbers

Precision: 0.5, Recall: 1.0 (see `data/ground_truth/precision_recall.json`)

Recall being perfect just means the method never wrongly says "different
person" when the answer is genuinely borderline at the 0.5 threshold - it
leans toward calling things a match. Precision at 0.5 is the real problem:
half of everything it flags as "same person" is actually two different people.

All 11 errors are conflation (two different people merged) - the worse kind,
since it corrupts both people's trust scores. Zero splitting errors this round.

## Failure mode 1: Coincidental time-slot overlap treated as identity

Example: `p2_e1` (Priya, cousin) vs `p6_e1` (mom) both fall on `sun_evening`.
Different people, same weekly time slot, one weak signal shared -> matched at
0.5. Time-of-day is a weak signal on its own; lots of unrelated people share
a day-of-week pattern purely by chance (Sunday evenings are just when the
wearer talks to family generally).

## Failure mode 2: Shared location, different actual person

Example: `p4_e1` (Sam, friend, climbing gym) vs `p7_e1` (Dev, gym friend,
also climbing gym, same evening slot) - matched at 0.667, the highest
conflation score in the set. Two different people who happen to share a
hobby and a regular time slot look almost identical to the current signal
set. This is the module's weakest case - overlapping location AND time,
no name to break the tie.

## Failure mode 3: Same first name, correctly treated as weak evidence, but still crosses threshold

Example: `p1_e3` (Priya, colleague) vs `p2_e1` (Priya, cousin) - matched at
0.5, right at the discount cap the module already applies for name-only
matches. The discount (capping name-only matches at 0.6) was meant to be
conservative, but 0.6 is still above the 0.5 decision threshold, so it
still gets counted as a match instead of correctly landing as "unsure,
don't merge."

## What's actually missing

- No signal currently *penalizes* a mismatch strongly enough. A missing
  location or a different location should count as real evidence *against*
  a match, not just as an absent signal - right now mismatches only remove
  potential matching signal, they don't push the probability down hard.
- The name-only discount cap (0.6) still sits above the 0.5 decision
  threshold, allowing name-only matches to be merged too easily.
- No signal-weighting: calendar_name, location, and time_slot are treated as
  equally informative, but they clearly aren't - a calendar name match is
  much stronger evidence than a shared time slot.
