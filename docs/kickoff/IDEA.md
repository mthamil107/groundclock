# GroundClock — Idea (Phase 0)

**One-liner:** A temporal grounding layer for LLMs, paired with **NowBench**, a benchmark
that measures whether a model actually *uses* the current date/time it was given — not just
whether the time was present in the prompt.

## Problem space (who feels the pain)

LLM application developers ship assistants that must reason about "now" — scheduling,
deadlines, "what's due this week", relative dates, timezone conversions. They inject the date
into the system prompt and assume it works. It often does not: even when the date is present,
models frequently ignore it ("temporal blindness"). The end user gets confidently wrong dates,
stale answers, and timezone errors. There is no standard way to (a) supply "now" reliably or
(b) test whether the model used it.

## What is actually broken (verified — see ../../RESEARCH.md)

- The model is stateless/frozen: it has **no clock and cannot store "now."** Apps inject
  date/time/timezone via the system prompt each request (Anthropic `currentDateTime`
  placeholder; leaked GPT-5.5 prompt). **This is the mechanism, not a bug.**
- **Temporal blindness (the real problem):** even when the date is injected, models often
  ignore it — no model >65% temporal alignment; timestamps appear in <4% of reasoning traces;
  deadline-closure 0.04 (inferred) vs 0.32 (injected). [arXiv 2511.09993, 2510.23853]
- Reported knowledge cutoffs are unreliable; effective cutoffs vary by topic [arXiv 2403.12958].
- Tool-augmented "time agents" recover most of the gap (SPAN ~95%) — validates the fix
  direction [arXiv 2511.09993].

## Novelty framing (HONEST — benchmark-first)

**This does NOT invent** structured prompt injection, tool/function calling, or timezone math
— those are established. The contribution is:

1. **NowBench (headline):** a benchmark that scores whether the model *uses* injected time —
   temporal alignment %, timestamp-usage rate in reasoning, cross-turn consistency — across
   task families (present-anchored date QA, timezone conversion, relative-time resolution,
   long-session staleness, deadline awareness). Prior benchmarks test temporal *knowledge*;
   NowBench tests temporal *grounding compliance*.
2. **GroundClock (reference layer):** a small, provider-agnostic middleware that gives the
   model a consistent, timezone-aware, monotonic, provenance-tagged "now" AND a
   `get_current_time` tool, so usage can be measured and improved.

The claim is not "these pieces are new"; it is "nobody has paired a *now-provisioning layer*
with a benchmark that measures whether the model actually *uses* the time." That gap is the work.

## Decisions (Phase 0)

| Item | Decision |
|---|---|
| Name | **GroundClock** (layer) + **NowBench** (benchmark) — both prior-art-checked, collision-free |
| Deliverable | arXiv preprint + open-source reference code |
| Framing | Benchmark-first; GroundClock is a reference integration |
| Eval scope | **Claude only** for v0 real numbers — Anthropic SDK, `claude-opus-4-8` (needs `ANTHROPIC_API_KEY`) |
| Audience | LLM application engineers (README) + temporal-reasoning researchers (paper) |
| Budget | ~1 month |

## Prior-work / naming check (Phase 0)

GitHub + web checked. **Rejected:** Chronos (Amazon time-series LLM + 9 others),
Sundial (thuml time-series foundation model), Tempora (existing PyPI datetime pkg),
Meridian (google ML framework). **Chosen: GroundClock** — zero collisions on GitHub/PyPI.
Full detail recorded in `docs/PRIOR-WORK.md`.

## Kill triggers / pivots

- **Kill/pivot** if NowBench shows **no measurable usage gap** on Claude (i.e., the model
  already uses injected time reliably) — then the paper becomes a negative-result note.
- **Pivot** if the gap exists but GroundClock's tool-based fix doesn't move the needle —
  reframe as a pure benchmark paper (still publishable).
- **Scope cut if behind:** drop multi-task-family breadth to the 2 strongest families;
  keep the metric + harness rigorous.
