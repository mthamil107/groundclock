# GroundClock — Project Plan

~1-month v0. Benchmark-first arXiv preprint + open-source reference implementation.

## Phases

| Week | Phase | Deliverable | Cut if behind |
|---|---|---|---|
| 1 | Spec + ref impl | `groundclock` package: temporal-context layer + `get_current_time` tool, CLI, smoke tests | Keep layer + tool; drop CLI polish |
| 2 | NowBench | 5 task families + metrics + runner (mock + Anthropic providers) | Drop to 2 strongest families (present-date, deadline) |
| 3 | Real eval | Run NowBench vs `claude-opus-4-8` across baseline / grounded / tool conditions | Single condition pair (baseline vs grounded) |
| 4 | Paper + launch | LaTeX paper, arXiv bundle, README, launch playbook | Ship paper draft; defer launch |

## Named milestones

- **M1 (end wk1):** `import groundclock` works; `pytest tests/unit` green; spec validates.
- **M2 (end wk2):** `nowbench run --provider mock` produces a metrics table with a measurable baseline↔grounded gap.
- **M3 (end wk3):** real `claude-opus-4-8` numbers in `results/` with no-match-probe footnote.
- **M4 (end wk4):** arXiv tarball builds < 50 MB; README audited.

## Kill triggers / pivots

- **Kill→negative-result note:** NowBench shows no measurable usage gap on Claude (model already uses injected time reliably).
- **Pivot→benchmark-only paper:** gap exists but GroundClock's tool layer doesn't improve usage.
- **Scope cut:** if wk2 slips, ship 2 task families, not 5; keep metric rigor.

## Risks

- API cost/access for real eval → mitigated by mock provider + small item counts.
- Grader brittleness on free-text answers → robust regex graders + manual spot-check sample.
- Over-claiming → enforced no-match probes in every family.
