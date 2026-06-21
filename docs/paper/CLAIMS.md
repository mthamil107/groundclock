# Claim verification — launch posts vs repo reality

Verify before posting. Status from the autopilot build.

| Claim (in posts/README/paper) | Verdict | Evidence |
|---|---|---|
| "Model has no clock; date is injected per request" | VERIFIED | RESEARCH.md (Anthropic docs, GPT-5.5 leak), framing in paper |
| "Temporal blindness: injected time under-used" | VERIFIED | RESEARCH.md (arXiv 2511.09993, 2510.23853); stated as prior-work, not our result |
| "Every gold item answerable only from injected now" | VERIFIED | `src/nowbench/tasks.py` — 5 families, gold derived from `frozen_now` |
| "No-match probes scored separately from alignment" | VERIFIED | `src/nowbench/metrics.py` (`scored_alignment` flag); `tests/conformance/test_nowbench.py` |
| "One clock behind block and tool" | VERIFIED | `src/groundclock/api.py` — both use `self._clock` |
| "Frozen-clock reproducibility + offline mock + Claude backend" | VERIFIED | `clock.py` FrozenClock; `providers/mock.py`; `providers/anthropic_provider.py` |
| "Apache-2.0" | VERIFIED | `LICENSE`, `pyproject.toml` |
| "14 tests passing" | VERIFIED | `python -m pytest` -> 14 passed |
| Mock example table (baseline 0 / grounded 100 / tool 100, tools 24) | VERIFIED | `nowbench run --provider mock --compliance 1.0` |
| **4-model OpenAI table** (gpt-4o-mini/4.1/5.1/5.5; baseline .10–.15, grounded .85–1.0, tool .90–1.0; tz_now .25–1.0; calibration 0 for all) | VERIFIED | `results/openai_*.json`, each produced by `nowbench run --provider openai --model <id>` |
| "non-monotonic timezone failure: small model beats larger ones" | VERIFIED | gpt-4o-mini tz .75 > gpt-4.1/gpt-5.1 tz .25 in the result files |
| "calibration uniformly absent across models" | VERIFIED | calibration = 0.00 in all four result files |
| Real `claude-opus-4-8` numbers | NEEDS RUN | no `ANTHROPIC_API_KEY`; paper presents the OpenAI models as the real runs and does NOT cite Claude numbers |

**Citations:** All 6 arXiv IDs verified against arXiv on 2026-06-21. Five were correct (titles/authors
cleaned up); one was mislabeled — `patqa2025` (arXiv 2504.00042) is *not* "present-anchored QA" but
"Beyond the Reported Cutoff: …Financial Knowledge" (Shah et al. 2025); corrected to `shah2025cutoff`
and re-cited as a knowledge-cutoff study. The 3 non-arXiv refs (Anthropic docs, GPT-5.5 leak,
Willison blog) are web sources.

**Recommendation:** POST AS DRAFTED. The paper now reports a real four-model run with verified
citations. Do not imply Claude numbers until that run exists. The non-monotonic timezone result and
universal calibration failure are the paper's sharpest honest findings.
