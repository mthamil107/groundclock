# Launch playbook — GroundClock

Order of operations. Do not start the public burst until the arXiv ID is live and the README is
audited.

## Step 0 — pre-flight
- [ ] `python -m pytest` green; `ruff check` clean; `verify_spec.py` and `run_microbench.py` run.
- [ ] Real `claude-opus-4-8` results committed to `results/anthropic_results.json` (or the post
      explicitly says results are forthcoming — do not imply numbers you don't have).
- [ ] Re-run the name check (`gh search repos "GroundClock"`, PyPI) — names can be taken late.
- [ ] README badges and status table match reality.

## Step 1 — arXiv
- [ ] Submit `docs/paper/arxiv-submission.tar.gz` (cs.CL). Wait for the ID.
- [ ] Put the arXiv ID in the README header and the repo description.

## Step 2 — coordinated burst (single day)
- [ ] Show HN (`02-show-hn.md`) — lead with the problem, not the project name.
- [ ] Tweet/X thread (`01-tweet-thread.md`).
- [ ] LinkedIn (`03-linkedin.md`).
- [ ] DMs to the named list (`04-dm-targets.md`), staggered.

## Step 3 — engage
- [ ] Reply to every substantive comment for the first few hours. Answer the "doesn't the model
      already know the date?" question with the framing, not defensiveness.

## Step 4 — upstream
- [ ] PR a provider (OpenAI/Gemini/Ollama) or open issues inviting them.
- [ ] PR to relevant "awesome-LLM-eval" / temporal-reasoning lists.

## Anti-patterns (do NOT)
- Don't post to multiple subreddits within the same hour.
- Don't quote-tweet your own thread to boost it.
- Don't DM 20 people in the same hour — stagger over a day or two.
- Don't edit the Show HN post after the first 30 minutes.
- Don't ask anyone to upvote.
- Don't claim numbers you haven't run. "Temporal blindness is documented; here's a benchmark to
  measure it on your model" is the honest pitch.
