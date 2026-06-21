# Prior-work & naming check

Checked GitHub (`gh search repos`) and the web (PyPI/general) on 2026-06-20 before committing
to a name.

## Rejected names (collisions)

| Name | Collision | Severity |
|---|---|---|
| **Chronos** | `amazon-science/chronos-forecasting` (pretrained LLM for time series), `Kodezi/Chronos` (debugging LLM), `cakephp/chronos` & `XiaoMi/chronos` (datetime/timestamp libs), `mesos/chronos` (scheduler) | Fatal — same time+ML space |
| **Sundial** | `thuml/Sundial` (time-series foundation model, ICML 2025 Oral), `LLNL/sundials` (ODE solver), `knowm/Sundial` (scheduler) | Fatal — same time+ML space |
| **Tempora** | `tempora` (existing PyPI datetime utility), `temporalio/temporal` (workflow engine) | High — PyPI name taken |
| **Meridian** | `google/meridian` (marketing-mix-model ML framework), `iliane5/meridian` (AI news) | Medium — prominent ML projects |

## Candidates that are clean

| Name | Result |
|---|---|
| **GroundClock** | Zero GitHub results; no PyPI package. **CHOSEN.** |
| Nowkit | Clean (only an unrelated 2015 reddit bot `eswedick/NowKith`) |
| TimeGround | Near-clean (one unrelated marketing site `ay-global/Timeground`) |

## Decision

- **Project / layer:** `GroundClock`
- **Benchmark:** `NowBench` (checked: no direct collision found; re-verify before PyPI/arXiv)
- PyPI package name to claim: `groundclock` (verify availability at publish time).

## Re-check before publishing

Names can be taken between now and launch. Re-run `gh search repos "GroundClock"` and
`WebSearch "groundclock" site:pypi.org` immediately before the README ships and before the
arXiv submission, per the launch checklist.
