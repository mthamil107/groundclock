# Results

- `mock_microbench.json` — offline mock run. Reproduce: `python scripts/run_microbench.py`.
- `openai_*.json` — **real runs**, four OpenAI models. Reproduce:
  ```bash
  pip install -e '.[openai]'   # set OPENAI_API_KEY
  for m in gpt-4o-mini gpt-4.1 gpt-5.1 gpt-5.5; do
    nowbench run --provider openai --model $m --json > results/openai_$m.json
  done
  ```

## Cross-model comparison (alignment by condition)

| model | baseline | grounded | tool | tz_now (grnd) | calibration |
|---|---|---|---|---|---|
| gpt-4o-mini | 0.10 | 0.95 | 1.00 | 0.75 | 0.00 |
| gpt-4.1 | 0.10 | 0.85 | 0.90 | 0.25 | 0.00 |
| gpt-5.1 | 0.15 | 0.85 | 1.00 | 0.25 | 0.00 |
| gpt-5.5 | 0.15 | 1.00 | 1.00 | 1.00 | 0.00 |

(20 gold items; calibration on 3 no-match probes, excluded from alignment; grounded consistency
1.00 for all four.)

**Findings:** (1) no model knows "now" (baseline 0.10–0.15); injection lifts all of them. (2) The
residual failure is timezone reasoning, and it is **non-monotonic** — the smallest model
(gpt-4o-mini, 0.75) beats two larger/newer ones (0.25). (3) A callable `get_current_time` tool
nearly closes every gap (1.00 for three of four; 0.90 for gpt-4.1). (4) **Calibration is 0 for every
model** — none ever abstains on the no-clock probes; each confabulates a date in all cases.

> Anthropic (`claude-opus-4-8`) run pending an API key:
> `nowbench run --provider anthropic --model claude-opus-4-8 --json > results/anthropic_results.json`
