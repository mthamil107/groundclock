# Findings Context — adjacent work and the gap

Distilled from `../../RESEARCH.md` (adversarially verified). Full citations there.

## What exists

- **Mechanism is settled.** Products inject date/time/timezone into the system prompt each
  request; the model has no clock (Anthropic `currentDateTime` placeholder; leaked GPT-5.5
  prompt). Knowledge cutoff is a separate fixed value.
- **Temporal *knowledge/reasoning* benchmarks.** TimeQA, TempReason, present-anchored
  temporal QA (PATQA), cross-calendar SPAN, "Dated Data" (effective vs reported cutoffs).
  These test what the model *knows* about time, and show it is largely unsolved
  (TimeQA best 46% vs human 87%; PATQA 1.5–16% EM).
- **Temporal *blindness* findings.** Even when the date is injected, models often ignore it:
  no model >65% alignment; timestamps in <4% of reasoning traces; deadline closure 0.04
  inferred vs 0.32 injected (arXiv 2511.09993, 2510.23853).
- **Mitigations.** System-prompt injection (deployed default); tool/function calling for a
  clock; web grounding. Tool-augmented "time agents" recover most of the SPAN gap (~95%).

## What they do well

- Knowledge benchmarks rigorously measure temporal *facts* and reasoning.
- The blindness papers prove the *use-it* problem is real and large.
- Time-agent results prove the *fix direction* (give the model a clock tool) works.

## The gap GroundClock fills

No one has shipped a **joint** artifact that (a) provides a consistent, timezone-aware,
provenance-tagged "now" to the model **and** (b) ships a benchmark whose metric is whether the
model *uses* the injected time — usage rate, alignment, cross-turn consistency — rather than
whether the time is merely present. NowBench is that benchmark; GroundClock is the reference
layer it scores.
