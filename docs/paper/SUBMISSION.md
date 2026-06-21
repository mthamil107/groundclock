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

The author is **already established in cs.CR** (3 prior papers), so a cs.CR submission needs **no
endorsement**, whereas cs.CL does. Recommended route — avoids the cs.CL endorsement gate:

```
Primary:     cs.CR          (no endorsement needed; the threat-model section justifies it)
Cross-list:  cs.CL, cs.AI   (cross-lists are moderator-reviewed, NOT endorsement-gated)
```

This lands the paper in the cs.CL listing without a cs.CL endorser. Caveats: (1) if cs.CR still
asks for endorsement, the 3 papers are likely < 3 months old (outside arXiv's "established"
window) and an endorser is needed anyway; (2) cross-lists are subject to moderation. If you instead
want **cs.CL primary**, you need a cs.CL endorsement (code VV3QKS) from another qualified user — you
cannot self-endorse.

## Pre-submission checklist
- [ ] `python scripts/build_arxiv.py` succeeds (< 50 MB).
- [ ] Title matches the rendered PDF title exactly.
- [ ] Abstract field is ASCII, no em-dash, no smart quotes, no `$...$`.
- [ ] Real results committed (or the paper/post states results are forthcoming).
- [ ] `claim-verify` pass on any launch post that cites repo features (see CLAIMS.md).
