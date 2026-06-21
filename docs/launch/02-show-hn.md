# Show HN

**Title:** Show HN: NowBench – does your LLM actually use the date you inject into its prompt?

**Body:**

LLMs have no clock. They're frozen at training time and stateless between calls, so they can't
know "now." Every product that seems to know the date — Claude, ChatGPT — is injecting it into the
system prompt on each request, separately from the model's training knowledge cutoff.

The catch: injecting the date is necessary but not sufficient. There's a documented failure mode
("temporal blindness") where the date is right there in context and the model still answers from
its training-era prior — wrong year, stale "today," deadlines treated as future when they've
passed.

NowBench measures whether the model *uses* the injected time, not whether it's present. Every gold
item is answerable only from the current instant (today's date, the time in another timezone right
now, "what date is 30 days from today," is a given deadline overdue). A correct answer is evidence
the clock was used. It ships with GroundClock, a small reference layer that supplies one
consistent, timezone-aware "now" through both a system-prompt block and a get_current_time tool
backed by the same clock.

It's honest by construction: every family includes no-match probes (no clock provided) where the
model should abstain; those are scored as calibration and never folded into the headline. There's
a frozen-clock mode for reproducibility and a deterministic offline mock so you can try it without
an API key, plus a Claude backend.

Apache-2.0. Code, spec, JSON Schema, threat model, and a short paper in the repo. I'd love for
people to run it against their model of choice and report the alignment number.

Repo: [link] · Paper: [arXiv link]
