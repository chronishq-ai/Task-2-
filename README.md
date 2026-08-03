# Pod B – Event Understanding Engine

Converts a plain-English event sentence into structured internal-state
signals (mood, focus, stress, confidence, trust, motivation, social_engagement)
for the Chronis-AI Core State Engine (Pod A) to consume.

## Architecture

```
config.py       Typed Settings, loaded once from .env
prompt.py       The single general-purpose prompt template
schemas.py      Pydantic models = the validation contract on model output
llm_client.py   Provider abstraction (GeminiProvider / AnthropicProvider)
logger.py       Append-only JSON log of every request/response
analyzer.py     analyze_event() — orchestrates prompt -> call -> validate -> retry -> log
main.py         CLI (single-shot or interactive)
test_events.py  Runs 15 realistic events end-to-end against the real API
tests/          Offline unit tests using a FakeProvider (no API key needed)
```

**Why it's split this way:** `analyzer.py` never imports `google.genai` or
`anthropic` directly — it only knows about the `LLMProvider` interface in
`llm_client.py`. Switching providers is a one-line config change
(`LLM_PROVIDER=anthropic` in `.env`), not a code change.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in GEMINI_API_KEY
```

## Usage

```python
from analyzer import analyze_event

analyze_event("I got promoted today.")
# {"signals": {"mood": {"value": 8.0, "confidence": 0.95}, ...}}
```

CLI:
```bash
python main.py "I got promoted today."
python main.py            # interactive loop
python test_events.py     # runs the 15-event batch, writes logs/test_events_summary.json
```

## Design decisions

- **Values, not deltas.** The prompt asks for the estimated *level* (0-10)
  of each variable after the event, with 5 as neutral, rather than a delta.
  This matches the example in the spec (`mood: 8`, not `mood: +3`). If Pod A
  actually needs deltas, only `prompt.py` needs to change.
- **Empty `signals` is valid.** Neutral events ("I bought milk") return
  `{"signals": {}}` instead of forcing a guess — this was called out
  explicitly in the prompt so the model doesn't hallucinate mood swings
  from grocery trips.
- **Confidence calibration is explicit in the prompt** (magnitude/ambiguity
  bands), not left to the model's default sense of confidence, since LLMs
  tend to cluster confidence scores near 0.8-0.9 regardless of actual
  ambiguity unless told otherwise.
- **Retry on both JSON and schema failures.** A response can be valid JSON
  but still violate the schema (e.g. `value: 15`, or an invented variable
  name) — both are treated as retryable, and the specific validation error
  is fed back to the model on the next attempt.
- **Markdown-fence stripping is defensive, not primary.** Gemini's
  `response_mime_type: application/json` config should prevent fences
  entirely; the stripping logic is a safety net in case that's ever bypassed
  or the provider is swapped for one without native JSON mode.
- **Every call is logged**, including failed ones (with the error message),
  to `logs/outputs.json`.

## Switching to Anthropic later

1. Set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` in `.env`.
2. Nothing else changes — `AnthropicProvider` in `llm_client.py` already
   implements the same `generate(prompt) -> str` interface as
   `GeminiProvider`.
