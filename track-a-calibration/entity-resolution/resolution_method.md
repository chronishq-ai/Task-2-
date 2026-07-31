# Entity Resolution - Method Spec

## The problem

Two of our variables are "trust in person A" and "trust in person B." If the
system can't reliably tell that this week's event about "Priya" is the same
Priya as last month's, both trust scores get corrupted. This is about
resolving identity from the wearer's side only - no voice or face recognition,
that's explicitly off limits (privacy, handled separately by Track B).

## Signals we're allowed to use

- **Calendar attendee names** - if an event has a calendar entry with a name attached
- **Recurring location** - same place showing up across multiple events (e.g. "coffee shop near office" appearing every Tuesday)
- **Name/relationship mentioned in speech** - wearer says "Priya" or "my sister"
- **Time pattern** - same day-of-week / time-of-day slot repeating

No biometric signal (voice print, face) is used anywhere in this.

## Test population

8 recurring people, spread across relationship types so we're testing real
ambiguity, not easy cases:

1. Priya - colleague (frequent, same coffee shop)
2. Priya - a *different* person, wearer's cousin (shared first name, on purpose)
3. Alex - partner
4. Sam - close friend
5. Rahul - colleague (mentioned only by relationship term sometimes: "my manager")
6. Mom - family, no name ever used, only "mom"
7. Dev - gym friend, low frequency, only 2 events
8. Alex - work project lead (different Alex, deliberately clashes with #3)

## What the module does

Input: two events (each with whatever wearer-side signal is attached).
Output: a probability that both events are about the same person, plus a
confidence in that probability.

This mirrors Sprint 1's shape - a value plus how sure we are - so scoring later
works the same way.
