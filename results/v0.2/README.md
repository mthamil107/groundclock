# NowBench v0.2 — multi-vendor results

6 models, 2 vendors (OpenAI + Google), added `user` injection-position condition and the
`fake_now` over-compliance (spoof) family. Reproduce (needs `OPENAI_API_KEY` / `GEMINI_API_KEY`):

```bash
pip install -e '.[openai,gemini]'
nowbench run --provider openai --model <id> --json > results/v0.2/openai_<id>.json
nowbench run --provider gemini --model <id> --json > results/v0.2/gemini_<id>.json
```

## Results

| model | baseline | grounded | user | tool | tz_now (grnd) | calibration | spoof-resist | spoof-adopt |
|---|---|---|---|---|---|---|---|---|
| gpt-4o-mini | 0.10 | 0.95 | 0.95 | 0.95 | 0.75 | 0.00 | 1.00 | 0.00 |
| gpt-4.1 | 0.10 | 0.90 | 0.90 | 0.90 | 0.50 | 0.00 | 1.00 | 0.00 |
| gpt-5.1 | 0.10 | 0.85 | 0.85 | 1.00 | 0.25 | 0.00 | 1.00 | 0.00 |
| gpt-5.5 | 0.15 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 0.00 |
| gemini-2.5-flash | 0.10 | 0.90 | 0.95 | 1.00 | 0.50 | 0.00 | 1.00 | 0.00 |
| gemini-2.5-pro | 0.10 | 0.95 | 0.95 | 0.90 | 0.75 | 0.00 | 1.00 | 0.00 |

(20 gold items; calibration on 3 no-match probes; spoof on 4 fake-now items.)

## Findings (honest, including two null results)

1. **No model knows "now" (baseline 0.10–0.15); injection helps all** (grounded 0.85–1.00) —
   confirmed across both vendors.
2. **Injection position does NOT matter (NULL).** grounded (system prompt) ≈ user (user turn) for
   every model. Whether the date is in the system prompt or the user turn, the model uses it the
   same. A clean negative result for the position ablation.
3. **Timezone reasoning is the real residual failure, and it is non-monotonic in tier.**
   tz_now(grounded) ranges 0.25–1.00; the smallest model (gpt-4o-mini, 0.75) beats gpt-5.1 (0.25).
   Now confirmed across two vendors.
4. **Calibration is 0.00 for ALL SIX models, both vendors.** On no-clock probes, none ever
   abstains — each confabulates a date. This is the strongest, most robust finding.
5. **Fake-now: 100% resistance, 0% adoption for all (NULL for over-compliance).** With an
   authoritative system-prompt clock present, every model resists a casual conflicting in-context
   date claim. The weak spoof does not elicit over-compliance; a stronger adversarial variant
   (a conflicting *tool* result, or an implausible injected date) is needed to probe this — future
   work.

**Caveats:** small suite (20 gold + 3 probes + 4 spoof); we cannot fully exclude provider-side
date injection. Anthropic (`claude-opus-4-8`) not included — account out of API credit.
