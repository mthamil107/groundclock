# Tweet / X thread

1/ Your LLM doesn't "know" today's date. It has no clock. The app pastes the date into the system
prompt every request. The real question isn't whether it *knows* the date — it's whether it
*uses* the one you gave it. Often it doesn't.

2/ This is "temporal blindness": the date is right there in context and the model still answers
from its training-era prior. Recent work finds injected timestamps show up in <4% of reasoning
steps and time-conditioned behavior barely improves when the time is present.

3/ So we built two things. GroundClock: a tiny layer that gives the model one consistent,
timezone-aware "now" via a system-prompt block AND a get_current_time tool — same clock behind
both, so they can't disagree.

4/ NowBench: a benchmark where every gold question is answerable ONLY from the injected now —
today's date, the time in Tokyo right now, "3 days from today", is this deadline past. A correct
answer is proof the model used the clock, not its memory.

5/ It's honest by construction: every family ships no-match probes (no clock given) where the
model should say "I can't determine that." Those are scored as calibration and never inflate the
headline number.

6/ Baseline vs grounded vs tool, with a frozen-clock mode for reproducibility and an offline mock
so you can run it without an API key. Apache-2.0.

7/ Paper + code + spec + threat model: [repo link] · [arXiv link]. Run it on your own model and
tell me what alignment you get.
