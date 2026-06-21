# Contributing to GroundClock

Thanks for your interest. GroundClock is small on purpose; contributions that keep it sharp are
very welcome.

## Good first contributions

- **New NowBench task families** — anything whose answer is derivable *only* from the current
  instant (e.g. business-day math, recurring-event "next occurrence", age-from-DOB).
- **New providers** — implement the `Provider` protocol (`src/groundclock/providers/base.py`):
  OpenAI, Gemini, Ollama, etc.
- **Adversarial probes** — "fake-now" injection probes (threat T1).

## Invariants you must keep

1. **No-match-probe honesty.** Every family must ship probes with no clock; the model should
   abstain. Probes are scored as calibration and must never be folded into alignment.
2. **Gold answers must require the injected now.** If an item is answerable from training data,
   it doesn't belong in a gold family.
3. **One clock.** The injected block and the tool must draw from the same `Clock`.

## Dev loop

```bash
pip install -e '.[dev]'
python -m pytest -q
python -m ruff check src tests scripts
python scripts/verify_spec.py
python scripts/run_microbench.py
```

All four must pass before a PR. Match the surrounding code's style and typing.
