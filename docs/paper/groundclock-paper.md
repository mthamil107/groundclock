# GroundClock: Measuring Whether Language Models Use the Current Time They Are Given

**Thamilvendhan Munirathinam** · Independent Researcher · mthamil107@gmail.com · <https://github.com/mthamil107>

**Abstract.**
Large language models are stateless and frozen at training time: they have no clock and cannot
know the current date. In deployment, applications supply the date by injecting it into the
system prompt on every request, and some additionally expose a clock as a callable tool. A
growing body of work shows that this injection is necessary but not sufficient — even when the
current time is present in context, models frequently fail to *use* it. We introduce
**GroundClock**, a small, provider-agnostic reference layer that supplies a consistent,
timezone-aware, provenance-tagged notion of "now" through both a system-prompt block and a
`get_current_time` tool drawn from a single clock, and **NowBench**, a benchmark whose every
gold item has an answer derivable *only* from the injected instant — so a correct answer is
direct evidence the model used the clock rather than its training-era prior. NowBench scores
*alignment* (did it use the injected time), *usage rate*, cross-turn *consistency*, and, via
deliberate no-match probes, *calibration*. Across four OpenAI models spanning two generations,
injecting the time raises alignment sharply, yet using it correctly for timezone reasoning remains
a failure that is *non-monotonic* in model tier (a small model beats two larger ones), and
calibration is *uniformly absent* — no model abstains when given no clock; a callable clock tool
nearly closes the gap. The contribution is not a new algorithm — date
injection, tool use, and timezone arithmetic are all standard — it is the pairing of a
now-provisioning layer with a benchmark that measures whether the injected time is actually
*used*, which prior work has not shipped jointly.

---

## 1. Introduction

A recurring confusion among practitioners is that a language model "secretly tracks" the date.
It does not. The model is a fixed function of its weights; each API call is independent and
carries no clock or cross-call memory. The appearance of date awareness comes entirely from the
application layer: products such as Claude and ChatGPT inject the current date, time, and
timezone into the system prompt on every request, holding the model's training *knowledge
cutoff* as a separate, fixed value. The interesting engineering and research question is
therefore not "does the model know the date" but **"does the model use the date it was given?"**

This distinction matters because the second question has an uncomfortable answer. Recent studies
report that models often ignore injected temporal information: across agentic traces, timestamps
appear in a small fraction of reasoning steps, and time-conditioned behaviors (such as treating a
deadline as passed) improve only modestly when the time is injected rather than inferred. We call
this **temporal blindness**: the gap between *having* the current time in context and *using* it.

We make the following contributions:

- **C1.** A precise framing that separates the model's (absent) clock, its fixed knowledge
  cutoff, and the application's per-request time injection — and identifies *use of injected
  time* as the measurable property of interest.
- **C2.** **GroundClock**, a reference temporal-grounding layer that exposes a single clock
  through both a system-prompt block and a `get_current_time` tool, with a structured,
  timezone-aware, provenance-tagged context object and a published JSON Schema.
- **C3.** **NowBench**, a benchmark of five task families in which every gold item is answerable
  only from the injected instant, scoring alignment, usage, and consistency.
- **C4.** A **calibration** protocol: every family ships no-match probes (no clock provided) on
  which the model should abstain; probes are scored separately and never inflate the headline.
- **C5.** A reproducible harness with a frozen-clock evaluation mode and a deterministic offline
  mock, plus a runnable Claude (`claude-opus-4-8`) backend.

## 2. Background

**Models are stateless and frozen.** Weights do not change after training; an inference call
retains nothing from a prior call. Consequently the model has no inherent "now".

**Knowledge cutoff is not a clock.** A model's training data ends at some point; this bounds what
it can know, but says nothing about the current date. Reported cutoffs are moreover unreliable:
*effective* cutoffs vary by topic and often precede the reported date \cite{cheng2024dated, shah2025cutoff}.

**Date is supplied by injection.** Deployed systems paste the current date/time/timezone into the
system prompt each request; provider documentation and leaked system prompts make the mechanism
explicit \cite{anthropic_sysprompt, gpt55leak, willison_claude4}. The knowledge cutoff is carried
separately.

**Temporal reasoning is hard and largely unsolved.** Benchmarks of temporal *knowledge* and
reasoning — TimeQA \cite{chen2021timeqa}, TempReason \cite{tan2023tempreason}, and cross-calendar
reasoning \cite{span2025} — report large gaps to
human performance. These measure what the model *knows*; they do not isolate whether an injected
*now* is used.

## 3. GroundClock and NowBench

### 3.1 The temporal context object

GroundClock builds a structured object (full schema in the repository) with fields: `instant`
(UTC, RFC 3339), `timezone` (IANA), `local_time`, `utc_offset` (DST-correct), `weekday`,
`sequence` (a monotonic per-session counter), `provenance` (`system_clock` / `injected` / `tool`
/ `unknown`), and an optional `knowledge_cutoff`. Two invariants matter for security and
correctness: (i) `local_time` converted to UTC equals `instant`; (ii) `sequence` is
non-decreasing within a session, so drift or a frozen clock is detectable.

### 3.2 Two surfaces, one clock

The object renders to a deterministic `<temporal_context>` block injected into the system prompt,
and the same clock backs a `get_current_time` tool. Because both draw from one `Clock`, they can
never disagree. A `FrozenClock` makes evaluation reproducible; a `SystemClock` is used in
production.

### 3.3 NowBench

NowBench has five families: **present_date** ("what is today's date"), **timezone_now** ("what
time is it right now in $Z$"), **relative_date** ("what date is $N$ days from today"),
**deadline** ("is a task due on $D$ overdue as of today"), and **consistency** (ask the date
twice in one session; answers must agree). Every gold item's answer is a function of the injected
instant alone, so it cannot be answered from training data — a correct answer is evidence of use.

Each item is run under three **conditions**: *baseline* (no time, no tool), *grounded*
(system-prompt block), and *tool* (block plus `get_current_time`).

**Metrics.** *Alignment* = correct / gold items (the headline). *Usage rate* = fraction whose
answer reflects the injected time. *Consistency* = stable date across turns. *Calibration* =
fraction of **no-match probes** (items deliberately given no clock) on which the model abstains;
probes are scored separately and never folded into alignment — this is what stops a writeup from
reporting "100% on $M$ items" when it is really "100% on $N$ of $M$, with $M-N$ probes excluded."

## 4. Evaluation

### 4.1 Reproducible offline harness

To validate the pipeline without an API key, NowBench ships a deterministic mock model
parameterized by a *compliance* rate — the fraction of items on which it uses an available clock
(and abstains when none is present) rather than confabulating from a stale training-era date.
This is a stand-in for measurement plumbing, not a claim about any real model.

At `compliance = 1.0` the mock is perfect when grounded and abstains correctly on probes; at the
baseline it has no clock and fails:

| condition | alignment | usage | consistency | calibration | tool calls |
|---|---|---|---|---|---|
| baseline | 0% | 0% | 0% | 100% | 0 |
| grounded | 100% | 100% | 100% | 100% | 0 |
| tool | 100% | 100% | 100% | 100% | 24 |

(20 gold items; calibration on 3 no-match probes, excluded from alignment.) Lowering compliance
reproduces partial temporal blindness, with grounded alignment tracking the compliance rate.
These numbers exercise the harness; the scientific result is the **real** run.

### 4.2 Real run: four OpenAI models

We evaluate four OpenAI models spanning two generations and a range of sizes
(`gpt-4o-mini`, `gpt-4.1`, `gpt-5.1`, `gpt-5.5`) under the three conditions; the knowledge-cutoff
field is omitted to avoid asserting an inaccurate value. Alignment by condition, plus two
diagnostics — grounded `timezone_now` alignment and probe calibration:

| model | baseline | grounded | tool | tz_now (grnd) | calibration |
|---|---|---|---|---|---|
| gpt-4o-mini | 0.10 | 0.95 | 1.00 | 0.75 | 0.00 |
| gpt-4.1 | 0.10 | 0.85 | 0.90 | 0.25 | 0.00 |
| gpt-5.1 | 0.15 | 0.85 | 1.00 | 0.25 | 0.00 |
| gpt-5.5 | 0.15 | 1.00 | 1.00 | 1.00 | 0.00 |

(20 gold items; calibration on 3 no-match probes, excluded from alignment. Grounded consistency is
1.00 for all four models.)

### 4.3 Findings

1. **No model knows "now"; injection helps all of them.** Baseline alignment is uniformly low
   (0.10–0.15) — confirming the absence of an internal clock across both generations — and rises
   sharply once the instant is injected (grounded 0.85–1.00).
2. **The residual failure is timezone reasoning, and it is non-monotonic in model tier.** Even with
   the current instant in context, `timezone_now` alignment ranges from 1.00 (gpt-5.5) down to 0.25
   (gpt-4.1, gpt-5.1) — and, strikingly, the smallest model (gpt-4o-mini, 0.75) *outperforms* two
   larger/newer ones. "Using the injected time correctly" does not track scale or recency; it is a
   distinct capability that this benchmark isolates.
3. **A clock tool nearly closes the gap.** Exposing `get_current_time` lifts tool alignment to
   1.00 for three of four models (0.90 for gpt-4.1), consistent with prior tool-augmentation
   results \cite{span2025}. Giving the model a clock it can *call* is more reliable than asking it
   to use a clock it was *shown*.
4. **Calibration is absent in every model.** On no-match probes (no clock provided), all four
   models abstain 0% of the time — each confabulates a current date in every case rather than
   admitting it cannot know one. This universal failure, across sizes and generations, is the
   sharpest result: not one model ever says "I don't know what today is."

**Caveats.** Four models on a small suite (20 gold items, 3 probes); a demonstration of the
protocol, not an exhaustive survey. We cannot fully exclude provider-side date injection by the
API, but the observed behavior — failing the frozen-date gold items and confabulating on the
probes — is consistent with no accurate clock being supplied by the API. Reproduce with
`nowbench run --provider openai --model <id>` for each model.

## 5. Threat model (condensed)

Because downstream logic depends on "now", a wrong or attacker-chosen time has security impact.
The authoritative source is the host `Clock`; anything read from the conversation is untrusted as
a time source. Key threats: **time spoofing via prompt injection** (CWE-345) — mitigated by
`provenance` tagging and the consistency metric; **timezone confusion** (CWE-697) — mitigated by
the local$=$UTC invariant and DST-correct offsets; **stale/replayed now** (CWE-294 analog) —
mitigated by the monotonic `sequence`. Clock-source compromise (NTP spoofing) is delegated to host
hardening. The full model is in the repository.

## 6. Related work

Temporal-knowledge benchmarks (TimeQA \cite{chen2021timeqa}, TempReason \cite{tan2023tempreason},
cross-calendar SPAN \cite{span2025}) measure what models know about time; "Dated Data"
\cite{cheng2024dated} and domain-cutoff studies \cite{shah2025cutoff} show reported cutoffs are
unreliable. The temporal-blindness study \cite{blindness2025} documents that injected time is
under-used. Tool-augmentation work shows a clock tool recovers much of the gap. GroundClock is
complementary: it assumes injection and tools exist, and supplies the missing piece — a benchmark
that scores whether the injected time is *used*, plus a reference layer to inject it consistently.

## 7. Discussion and future work

NowBench v0 is intentionally small and deterministic. Planned work: adversarial "fake-now" probes
(measuring resistance to time spoofing), detection of timestamp usage inside reasoning traces,
multi-turn agent traces, and additional providers for a cross-model leaderboard. We expect the
most valuable artifact to be the *protocol* — usage and calibration reported together — rather
than any single number.

## 8. Conclusion

The premise that a language model "tracks" the date is a misreading of a real phenomenon: the date
is supplied externally, every request, and is often not used. GroundClock supplies it consistently
through one clock and two surfaces; NowBench measures whether it is used, honestly. The
contribution is not a new algorithm but a benchmark-and-reference pairing that turns "temporal
blindness" from an anecdote into a number you can track.

## Reproducibility

Code, spec, schema, threat model, and harness: <https://github.com/mthamil107/groundclock>.
`python -m pytest`, `python scripts/verify_spec.py`, and `python scripts/run_microbench.py`
reproduce the offline results; `nowbench run --provider openai --model <id>` reproduces the
model runs.
