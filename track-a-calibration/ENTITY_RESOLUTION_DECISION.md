# Entity Resolution Decision - Track A, Sprint 2

## Result

```
Precision: 0.5
Recall:    1.0
```

## Against the doctrine's thresholds

- **>90% accuracy** -> approach is sound
- **<80%** -> needs a hybrid approach or redesign

Precision of 0.5 is well under 80%. **This does not clear the bar as-is.**

## What this means (and doesn't mean)

This is not a hard gate on the sprint - Track C integrates regardless, using
an explicit "entity resolution confidence" field. But the honest read is:
the current signal set (calendar name, location, mentioned name/relationship,
time slot) is not enough on its own to reliably tell people apart, especially
when two different people share a first name or a regular time/location
pattern (see `FAILURE_MODES.md` for concrete cases).

All 11 errors were conflation (merging two different people) - the more
harmful failure type, since it corrupts both people's trust variables rather
than just fragmenting one person's history.

## Why precision is weak, in one line

Weak signals (a shared time slot, a shared location) currently count as
positive evidence with no matching penalty for signals that *don't* match,
and the name-only match discount lands exactly on the 0.5 decision boundary
instead of clearly below it.

## Recommendation for Track C integration

Given the low precision, recommend:

1. **Raise the same-person threshold** from 0.5 to something stricter (e.g.
   0.75+) until the scoring function itself improves - fewer false merges,
   more cases correctly left as "unresolved," which is safer than a wrong
   merge.
2. **Weight signals unevenly** - calendar_name should count for much more
   than time_slot alone. This alone should fix most of the observed failures.
3. **Add an explicit "unresolved" state** rather than forcing every pair into
   same/different - Track C's schema should be able to hold "we don't know
   yet" rather than defaulting to a guess.
4. Track C should treat the entity-resolution confidence field as **low
   trust** for now, and avoid letting a single low-confidence resolution
   silently overwrite an established trust score.

## What's confirmed working end-to-end

- Method spec written, 8-person test population built with deliberate
  ambiguity (shared names, relationship-only references).
- Resolution module runs, produces probability + confidence per pair.
- Full pairwise run completed - 136 pairs across 17 events.
- Precision/recall computed against real (constructed) ground truth.
- Failure modes documented with concrete examples, not just aggregate numbers.
