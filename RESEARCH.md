# Temporal Grounding in LLMs — Research Foundation

Cited research backing the paper. Generated via adversarial multi-source verification
(21 sources fetched, 90 claims extracted, 25 verified by 3-vote, 23 confirmed, 2 killed).

## Thesis verdict on the original premise

- **"The LLM stores the date (bug)" — FALSE.** LLMs are stateless and frozen; no internal
  clock, no cross-call memory. The model cannot store "now."
- **"It keeps track of the date" — TRUE, but it's the *application* doing it.** Products
  inject current date/time/timezone into the **system prompt** every request, held
  *separately* from a fixed, model-specific knowledge cutoff.
- **"This is fragile" — TRUE, and the real contribution.** Even when the date is injected,
  models frequently ignore it ("temporal blindness").

## RQ1 — Mechanism (CONFIRMED, high confidence)

Date/time/timezone is injected via the system prompt; the model does not store it; the
knowledge cutoff is a separate fixed value.

- Anthropic system-prompt docs: verbatim `currentDateTime` placeholder; model framed as an
  "informed individual" at a fixed cutoff. — https://platform.claude.com/docs/en/release-notes/system-prompts
- Leaked GPT-5.5 prompt injects `Current date` + `timezone` (e.g. Atlantic/Reykjavik) with
  cutoff (2025-08) held separately. — https://github.com/asgeirtj/system_prompts_leaks/blob/main/OpenAI/gpt-5.5-thinking.md
- Corroboration: Simon Willison's Claude-4 system-prompt analysis (blog);
  OpenAI community thread on an invalid injected cutoff (forum).
  - https://simonwillison.net/2025/May/25/claude-4-system-prompt/
  - https://community.openai.com/t/gpt-5-4-system-prompt-contains-invalid-cutoff-of-2024-06/1378620

## RQ2/RQ3 — Literature, benchmarks, failure modes (CONFIRMED, NUANCED + FRAGILE)

- **Reported cutoffs are unreliable; effective cutoffs vary by topic** ("Dated Data"):
  Llama-3-70B ~54% on 2017 facts vs ~6% on 1995 facts. — https://arxiv.org/abs/2403.12958
- **Temporal QA largely unsolved:** TimeQA best model 46% vs human 87%
  (https://arxiv.org/abs/2108.06314); cross-calendar SPAN — Miao, Fu, Wei 2025
  (https://arxiv.org/abs/2511.09993). TempReason / time-sensitive QA motivation:
  https://arxiv.org/abs/2306.08952
  - **Citation correction (verified 2026-06-21):** arXiv 2504.00042 is *not* a "present-anchored
    QA" paper — it is "Beyond the Reported Cutoff: Where LLMs Fall Short on Financial Knowledge"
    (Shah et al. 2025), a domain knowledge-cutoff study. The earlier "PATQA 1.5–16% EM" label was a
    research-pass error and has been removed; the paper cites 2504.00042 correctly as a cutoff study.
- **Temporal blindness (KEY):** even with injected timestamps, models largely ignore them —
  no model above ~65% alignment, timestamps in <4% of reasoning traces; deadline closure
  0.04 inferred vs 0.32 injected. — https://arxiv.org/pdf/2511.09993 , https://arxiv.org/html/2510.23853v2
- Additional failure-mode sources: https://arxiv.org/pdf/2503.17073 , https://arxiv.org/pdf/2506.05790

## RQ4/RQ5 — Mitigations and the gap (CONFIRMED)

- **Tool-augmented agents recover most of the gap:** SPAN "Time Agent" ~95.31% (vs ~34.5
  six-model no-tool avg). — https://arxiv.org/pdf/2511.09993
- Deployed mitigation today = system-prompt injection (+ web/tool grounding):
  https://www.damiangalarza.com/posts/2026-01-07-llm-date-time-context-production/ ,
  https://www.digitalocean.com/community/tutorials/web-grounding-llms ,
  https://www.theregister.com/2024/08/26/ai_llm_tool_calling/
- **GAP / white space:** no joint "temporal grounding layer" (consistent, timezone-aware,
  provenance-tagged `now`) paired with a benchmark that tests whether the model *uses* the
  injected time — not merely whether it is present.

## Claims that FAILED verification (do NOT put in the paper)

- "Large impact of explicit temporal feedback *falsifies* internal time-tracking" — killed
  1-2 (over-strong causal claim). Keep framing as mechanistic, not a falsification proof.
- "Models systematically hallucinate 'last Tuesday' / 'since our last chat' contradictions"
  — killed 1-2 (over-generalized). Don't assert as established fact.

## Caveats for honest related-work

Several failure-mode results come from single, unreplicated papers, some Qwen3-only. State
sample/model scope when citing. OpenAI prompt evidence is a community leak repo (not primary);
Anthropic evidence is primary docs.
