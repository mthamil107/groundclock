# arXiv submission fields — paste-ready

Title is consistent across `groundclock-paper.md`, `groundclock-paper.tex`, and the README.
The blocks below are cleaned for arXiv's form: no em-dashes (use `--`), straight quotes only,
no LaTeX math.

## Title (paste into Title field)

```
GroundClock: Measuring Whether Language Models Use the Current Time They Are Given
```

## Abstract (paste into Abstract field; ASCII, no em-dash, under 1920 chars)

```
Large language models are stateless and frozen at training time: they have no clock and cannot
know the current date. In deployment, applications supply the date by injecting it into the system
prompt on every request, and some additionally expose a clock as a callable tool. A growing body of
work shows this injection is necessary but not sufficient -- even when the current time is present
in context, models frequently fail to use it. We introduce GroundClock, a small, provider-agnostic
reference layer that supplies a consistent, timezone-aware, provenance-tagged notion of "now"
through both a system-prompt block and a get_current_time tool drawn from a single clock, and
NowBench, a benchmark whose every gold item has an answer derivable only from the injected instant,
so a correct answer is direct evidence the model used the clock rather than its training-era prior.
NowBench scores alignment (did it use the injected time), usage rate, cross-turn consistency, and,
via deliberate no-match probes, calibration. Across four OpenAI models spanning two generations,
injecting the time raises alignment sharply, yet using it correctly for timezone reasoning remains a
failure that is non-monotonic in model tier (a small model beats two larger ones), and calibration
is uniformly absent -- no model abstains when given no clock; a callable clock tool nearly closes the
gap. The contribution is not a new algorithm -- date injection, tool use, and timezone arithmetic are
all standard -- it is the pairing of a now-provisioning layer with a benchmark that measures whether
the injected time is actually used, which prior work has not shipped jointly.
```

## Comments (paste into Comments field; under 400 chars)

```
Code, spec, JSON Schema, and reproducible harness (offline mock + Claude backend) included. v0 preview.
```

## Author metadata (matches arXiv account)

```
Name:        Thamilvendhan Munirathinam
Affiliation: Independent Researcher
Email:       mthamil107@gmail.com
URL:         https://github.com/mthamil107
Country:     India
```

## Primary category

Your arXiv account default is **cs.CR**. For this paper the best fit is **cs.CL** (it is an
LLM/benchmark paper); cs.CR is reasonable as a cross-list because of the threat-model section, but
cs.CR moderators may reclassify a benchmark paper. Recommendation:

```
Primary:     cs.CL          (switch from your cs.CR default on the submission form)
Cross-list:  cs.CR, cs.AI
```

If you prefer the security framing to lead, keeping **cs.CR** primary with cs.CL + cs.AI cross-lists
is acceptable — just expect possible moderator reclassification toward cs.CL.

## Pre-submission checklist
- [ ] `python scripts/build_arxiv.py` succeeds (< 50 MB).
- [ ] Title matches the rendered PDF title exactly.
- [ ] Abstract field is ASCII, no em-dash, no smart quotes, no `$...$`.
- [ ] Real results committed (or the paper/post states results are forthcoming).
- [ ] `claim-verify` pass on any launch post that cites repo features (see CLAIMS.md).
