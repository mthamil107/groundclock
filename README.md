# GroundClock

**A temporal grounding layer for LLMs — plus NowBench, a benchmark that measures whether a model actually *uses* the current date/time it was given.**

[![tests](https://img.shields.io/badge/tests-14%20passing-brightgreen)](tests/)
[![license](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![status](https://img.shields.io/badge/status-v0%20preview-orange)]()

[Spec](docs/spec/v0.md) · [Security](docs/THREATS.md) · [Paper](docs/paper/groundclock-paper.md) · [Research basis](RESEARCH.md)

> **13-second explainer GIF** — _placeholder; record with screen capture before launch._

## What this is NOT

GroundClock is **not** a new way to make a model "know" the date, and it does **not** claim that
injecting the date or giving the model a clock tool is novel — both are standard practice. It is a
**measurement-and-reference layer**: a benchmark whose metric is whether the model *uses* the time
it was handed, plus a small reference implementation of a consistent, timezone-aware "now" so that
usage can be measured and improved.

## Why this is different

1. **It measures use, not presence.** Existing temporal benchmarks (TimeQA, TempReason, …) test
   what a model *knows* about time. NowBench tests whether it *uses* the `now` you inject —
   because the documented failure is that models often ignore it ("temporal blindness").
2. **Every gold item is only answerable from the injected now.** Today's date, the time in another
   timezone *right now*, "3 days from today", whether a deadline has passed — none are answerable
   from training data, so a correct answer is direct evidence the clock was used.
3. **Honest by construction.** Every family ships no-match probes (no clock provided); the model
   should abstain. Probes are scored as *calibration* and never folded into the headline alignment.
4. **One clock, two surfaces.** The injected system-prompt block and the `get_current_time` tool
   draw from the same `Clock`, so they can never disagree — and a `FrozenClock` makes runs
   reproducible.

## What this does NOT claim to invent

System-prompt date injection, tool/function calling, and `zoneinfo` timezone math are all
established techniques. The contribution is not those pieces — it is **pairing a now-provisioning
layer with a benchmark that scores whether the model uses the injected time**, which the research
survey in [`RESEARCH.md`](RESEARCH.md) found nobody had shipped jointly.

## Status

| Component | State |
|---|---|
| Temporal-context spec + JSON Schema | ✅ shipped (`docs/spec/v0.md`) |
| `groundclock` layer (`GroundClock`, `get_current_time`, CLI) | ✅ shipped |
| NowBench (5 families, 3 conditions, metrics) | ✅ shipped |
| Mock provider (offline) | ✅ shipped |
| Anthropic + OpenAI providers | ✅ shipped (need the matching API key) |
| Real results: 4 OpenAI models | ✅ shipped (`results/openai_*.json`; gpt-4o-mini / gpt-4.1 / gpt-5.1 / gpt-5.5) |
| Real results: `claude-opus-4-8` | ⏳ pending — needs `ANTHROPIC_API_KEY` |
| Threat model | ✅ shipped (`docs/THREATS.md`) |
| Paper / arXiv bundle | ✅ draft (`docs/paper/`) |

## Install

```bash
git clone https://github.com/groundclock/groundclock
cd groundclock
pip install -e '.[dev]'            # core + test deps
pip install -e '.[anthropic]'     # add the Claude backend
```

## Quickstart

```python
from groundclock import GroundClock

gc = GroundClock(tz="America/New_York", knowledge_cutoff="2026-01")

# 1. Inject a consistent "now" into your system prompt:
system = "You are a helpful assistant.\n\n" + gc.system_block()

# 2. ...and/or expose the tool, drawing from the SAME clock:
tools = [gc.tool_spec()]                 # pass to Messages API `tools`
# on a get_current_time tool_use: handler returns the context as JSON
result = gc.handle_tool_call({"timezone": "Asia/Tokyo"})
```

CLI:

```bash
groundclock now --tz America/New_York --cutoff 2026-01
groundclock now --json
```

## How it feels to use

```
You (the app)                       GroundClock (under the hood)
-----------------------------       ------------------------------------------
gc.system_block()             --->  reads Clock once, builds TemporalContext,
                                    renders a byte-stable <temporal_context> block
prompt = base + block         --->  the model now sees an authoritative "now"
gc.tool_spec() in tools       --->  same Clock backs get_current_time
model calls get_current_time  --->  gc.handle_tool_call() answers from that Clock
```

You do **not** have to recompute or re-pass the date every turn yourself — `GroundClock` owns the
clock and the rendering, and advances a monotonic `sequence` so drift is detectable.

## Run NowBench

```bash
# Offline, no API key — demonstrates the baseline vs grounded vs tool gap:
python scripts/run_microbench.py

# Real model:
nowbench run --provider anthropic --model claude-opus-4-8
```

Example (offline mock, `compliance=1.0` — a model that always uses an available clock):

```
condition   alignment    usage  consist   calib  tools
------------------------------------------------------
baseline           0%       0%       0%    100%      0
grounded         100%     100%     100%    100%      0
tool             100%     100%     100%    100%     24
```

> The mock is a deterministic stand-in for offline testing. Lower `--compliance` to simulate
> temporal blindness. Real numbers come from the Anthropic provider.

## Architecture

```
+-----------------------------+        +----------------------------+
|        groundclock          |        |          nowbench          |
|  Clock (System/Frozen)      |        |  tasks (5 families)        |
|  TemporalContext + render   |<-------|  grader (parse + score)    |
|  GroundClock facade         |        |  metrics (alignment/usage) |
|  get_current_time tool      |        |  runner (3 conditions)     |
|  providers (mock/anthropic) |------->|                            |
+-----------------------------+        +----------------------------+
```

## Concepts

- **Temporal Context** — the structured `now` object ([spec](docs/spec/v0.md)).
- **Alignment** — fraction of gold items answered correctly (the headline "uses the clock").
- **Usage rate** — fraction where the answer reflects the injected time.
- **Calibration** — fraction of no-match probes the model correctly abstains on.
- **Consistency** — does the date stay stable across turns in a session.
- **Temporal blindness** — the model ignoring injected time even when present (the problem).

## How this relates to existing work

| Project | Tests | GroundClock difference |
|---|---|---|
| TimeQA / TempReason | temporal *knowledge* & reasoning | tests whether injected *now* is *used* |
| "Dated Data" | effective vs reported cutoffs | orthogonal; we assume injection, measure use |
| Time-agent papers | tool-augmented accuracy | we ship the joint layer + a usage metric |

Full cited basis in [`RESEARCH.md`](RESEARCH.md).

## Roadmap

- **v0.2** — adversarial "fake-now" probes (T1 in the threat model); `tz` validation; OpenAI/Gemini/Ollama providers.
- **v0.5** — multi-turn agent traces; timestamp-usage detection in reasoning traces.
- **v1.0** — stable spec; published multi-model leaderboard.

## Security

See [`docs/THREATS.md`](docs/THREATS.md) — time spoofing, timezone confusion, stale/replayed clocks.

## Contributing

Issues and PRs welcome — new task families and providers especially. Please keep the no-match-probe
honesty invariant.

## License

Apache-2.0 — see [`LICENSE`](LICENSE).

## Prior work and naming

Named **GroundClock** after a prior-art check ([`docs/PRIOR-WORK.md`](docs/PRIOR-WORK.md)) rejected
"Chronos" (Amazon's time-series model + datetime libraries), "Sundial" (a time-series foundation
model), and "Tempora" (an existing PyPI package).
